"""
Day 9 S2 — LangGraph Agent with Approval Gate
==============================================
Implements StateGraph with MemorySaver for multi-turn conversations.

Features:
- Multi-turn thread memory (thread_id)
- Approval gate for >3 kW systems (subsidy capped)
- Router → Tool → Approval → RAG → Synthesize workflow
- Fallback state machine if LangGraph not installed

Run with:
    python -m app.graph
"""

from typing import TypedDict, Optional, List, Dict, Any, Literal
import json

# Try to import LangGraph
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: langgraph not installed. Using fallback state machine.")

from app.tools import extract_capacity_kw, solar_cfa_calculator
from app.rag import answer_question


# Define Agent State
class AgentState(TypedDict):
    """State for the agent graph."""
    question: str
    thread_id: str
    capacity_kw: Optional[float]
    requires_approval: bool
    approved: bool
    approval_status: str
    tool_output: Dict[str, Any]
    rag_output: Dict[str, Any]
    citations: List[Dict[str, Any]]
    tools_used: List[str]
    answer: str
    history: List[Dict[str, str]]
    current_node: str


# Global memory storage (simple dict-based for fallback)
_memory_store: Dict[str, List[Dict[str, str]]] = {}


def router_node(state: AgentState) -> AgentState:
    """
    Router node: Extract capacity and determine workflow path.
    
    Decisions:
    - Extract capacity_kw from question
    - Check if capacity > 3.0 (requires approval)
    - Determine which tools to call
    """
    question = state["question"]
    thread_id = state.get("thread_id", "default")
    
    # Extract capacity
    capacity = extract_capacity_kw(question)
    
    # Check history for previous capacity mentions
    history = state.get("history", [])
    if not capacity and history:
        for turn in reversed(history):
            if "capacity" in turn.get("question", "").lower():
                prev_capacity = extract_capacity_kw(turn["question"])
                if prev_capacity:
                    capacity = prev_capacity
                    break
    
    state["capacity_kw"] = capacity
    state["current_node"] = "router"
    
    # Determine if approval needed (capacity > 3 kW or cost/payback query)
    q_lower = question.lower()
    cost_keywords = ["cost", "price", "payback", "install", "vendor quote"]
    
    if capacity and capacity > 3.0:
        state["requires_approval"] = True
        state["approval_status"] = "pending"
    elif any(kw in q_lower for kw in cost_keywords):
        state["requires_approval"] = True
        state["approval_status"] = "pending"
    else:
        state["requires_approval"] = False
        state["approval_status"] = "not_required"
    
    return state


def tool_node(state: AgentState) -> AgentState:
    """
    Tool node: Execute solar_cfa_calculator.
    
    Runs calculator if capacity is available.
    """
    capacity = state.get("capacity_kw")
    
    if capacity and capacity > 0:
        try:
            calc_result = solar_cfa_calculator(
                capacity_kw=capacity,
                special_category_state=False,
                monthly_bill_inr=2000.0
            )
            
            state["tool_output"] = {"solar_cfa_calculator": calc_result}
            
            if "tools_used" not in state:
                state["tools_used"] = []
            state["tools_used"].append("solar_cfa_calculator")
            
        except Exception as e:
            state["tool_output"] = {"error": str(e)}
    else:
        state["tool_output"] = {"skipped": "No capacity found"}
    
    state["current_node"] = "tool"
    return state


def approval_node(state: AgentState) -> AgentState:
    """
    Approval gate: Check if user approved high-capacity or cost queries.
    
    If requires_approval and not approved:
    - Return pending approval message
    
    If approved:
    - Continue with workflow
    """
    requires_approval = state.get("requires_approval", False)
    approved = state.get("approved", True)  # Default to True if not specified
    capacity = state.get("capacity_kw", 0)
    
    if requires_approval and not approved:
        # User needs to confirm
        state["approval_status"] = "pending"
        state["answer"] = (
            f"⚠️ **Approval Required**\n\n"
            f"You've requested a {capacity} kW system. "
            f"Please note that CFA subsidy is capped at 3 kW (₹78,000 maximum for general states). "
            f"The system cost beyond 3 kW will be fully paid by you.\n\n"
            f"Do you want to proceed with this configuration?\n\n"
            f"To confirm, please send your request again with approval=True in the API call."
        )
        state["current_node"] = "approval"
        return state
    
    # Approved or not required
    state["approval_status"] = "approved" if requires_approval else "not_required"
    state["current_node"] = "approval"
    return state


def rag_node(state: AgentState) -> AgentState:
    """
    RAG node: Retrieve policy guidelines and citations.
    
    Calls answer_question from app/rag.py.
    """
    question = state["question"]
    
    try:
        rag_result = answer_question(question, top_k=4)
        
        state["rag_output"] = rag_result
        state["citations"] = rag_result.get("citations", [])
        
        if "tools_used" not in state:
            state["tools_used"] = []
        state["tools_used"].append("answer_question")
        
    except Exception as e:
        state["rag_output"] = {"error": str(e), "answer": "RAG lookup failed."}
        state["citations"] = []
    
    state["current_node"] = "rag"
    return state


def synthesize_node(state: AgentState) -> AgentState:
    """
    Synthesize node: Combine tool outputs and RAG to create final answer.
    
    Also updates conversation history.
    """
    question = state["question"]
    tool_output = state.get("tool_output", {})
    rag_output = state.get("rag_output", {})
    citations = state.get("citations", [])
    thread_id = state.get("thread_id", "default")
    
    # Build answer from components
    answer_parts = []
    
    # Add calculator results if available
    if "solar_cfa_calculator" in tool_output:
        calc = tool_output["solar_cfa_calculator"]
        
        answer_parts.append(
            f"**Solar System Configuration for {calc['capacity_kw']} kW:**\n\n"
        )
        
        answer_parts.append(
            f"• **CFA Subsidy:** ₹{calc['cfa_subsidy_inr']:,.0f}"
        )
        
        if calc['capped']:
            answer_parts.append(" ⚠️ (Capped at 3 kW - no additional CFA beyond 3 kW)")
        
        answer_parts.append(
            f"\n• **Shadow-free Roof Area:** {calc['shadow_free_area_sq_m']} sq m "
            f"({calc['shadow_free_area_sq_ft']} sq ft)"
        )
        
        answer_parts.append(
            f"\n• **MNRE Benchmark Cost:** ₹{calc['benchmark_cost_inr']:,.0f}"
        )
        
        answer_parts.append(
            f"\n• **Net Cost (after CFA):** ₹{calc['net_cost_inr']:,.0f}"
        )
        
        if calc['estimated_payback_years']:
            answer_parts.append(
                f"\n• **Estimated Payback:** {calc['estimated_payback_years']} years"
            )
        
        answer_parts.append("\n\n")
    
    # Add RAG answer if available
    if "answer" in rag_output:
        rag_answer = rag_output["answer"]
        
        if answer_parts:
            answer_parts.append("**Additional Guidelines:**\n\n")
        
        answer_parts.append(rag_answer)
    
    # Add citations
    if citations and len(citations) > 0:
        answer_parts.append("\n\n**Sources:**\n")
        for i, cite in enumerate(citations[:3], 1):
            answer_parts.append(
                f"{i}. {cite['title']} (Page {cite['page']})\n"
            )
    
    # Fallback
    if not answer_parts:
        answer_parts.append(
            "I don't have enough information to answer this question. "
            "Please ask about PM Surya Ghar CFA subsidy calculations or guidelines."
        )
    
    final_answer = "".join(answer_parts)
    state["answer"] = final_answer
    
    # Update history
    if "history" not in state or state["history"] is None:
        state["history"] = []
    
    state["history"].append({
        "question": question,
        "answer": final_answer,
    })
    
    # Save to memory store
    global _memory_store
    _memory_store[thread_id] = state["history"]
    
    state["current_node"] = "synthesize"
    return state


def should_continue_after_approval(state: AgentState) -> Literal["rag", "end"]:
    """Decide if workflow continues after approval gate."""
    approval_status = state.get("approval_status", "not_required")
    
    if approval_status == "pending":
        return "end"  # Stop and wait for user approval
    else:
        return "rag"  # Continue to RAG node


def build_graph() -> Any:
    """Build LangGraph StateGraph with approval gate."""
    if not LANGGRAPH_AVAILABLE:
        return None
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("tool", tool_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("synthesize", synthesize_node)
    
    # Define edges
    workflow.set_entry_point("router")
    workflow.add_edge("router", "tool")
    workflow.add_edge("tool", "approval")
    
    # Conditional edge after approval
    workflow.add_conditional_edges(
        "approval",
        should_continue_after_approval,
        {
            "rag": "rag",
            "end": END,
        }
    )
    
    workflow.add_edge("rag", "synthesize")
    workflow.add_edge("synthesize", END)
    
    # Compile with memory
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)
    
    return graph


def run_graph_agent(
    question: str,
    thread_id: str = "default",
    approved: bool = True,
    special_category_state: bool = False,
) -> Dict[str, Any]:
    """
    Run the LangGraph agent with approval gate and memory.
    
    Args:
        question: User question
        thread_id: Thread ID for multi-turn memory
        approved: Whether user approved high-capacity/cost queries
        special_category_state: True for special category states
    
    Returns:
        Dictionary with answer, tools_used, citations, approval_status, history
    """
    # Load history from memory
    global _memory_store
    history = _memory_store.get(thread_id, [])
    
    # Initialize state
    initial_state: AgentState = {
        "question": question,
        "thread_id": thread_id,
        "capacity_kw": None,
        "requires_approval": False,
        "approved": approved,
        "approval_status": "not_required",
        "tool_output": {},
        "rag_output": {},
        "citations": [],
        "tools_used": [],
        "answer": "",
        "history": history,
        "current_node": "start",
    }
    
    if LANGGRAPH_AVAILABLE:
        # Use LangGraph
        graph = build_graph()
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            result = graph.invoke(initial_state, config)
            
            return {
                "question": result["question"],
                "answer": result["answer"],
                "tools_used": result.get("tools_used", []),
                "tool_output": result.get("tool_output", {}),
                "citations": result.get("citations", []),
                "approval_status": result.get("approval_status", "not_required"),
                "requires_approval": result.get("requires_approval", False),
                "thread_id": thread_id,
                "history": result.get("history", []),
            }
        
        except Exception as e:
            return {
                "question": question,
                "answer": f"Graph execution error: {str(e)}",
                "tools_used": [],
                "tool_output": {},
                "citations": [],
                "approval_status": "error",
                "requires_approval": False,
                "thread_id": thread_id,
                "history": history,
                "error": str(e),
            }
    
    else:
        # Fallback: run nodes sequentially
        state = initial_state
        
        try:
            state = router_node(state)
            state = tool_node(state)
            state = approval_node(state)
            
            # Check if pending approval
            if state["approval_status"] == "pending":
                return {
                    "question": state["question"],
                    "answer": state["answer"],
                    "tools_used": state.get("tools_used", []),
                    "tool_output": state.get("tool_output", {}),
                    "citations": [],
                    "approval_status": "pending",
                    "requires_approval": True,
                    "thread_id": thread_id,
                    "history": state.get("history", []),
                }
            
            state = rag_node(state)
            state = synthesize_node(state)
            
            return {
                "question": state["question"],
                "answer": state["answer"],
                "tools_used": state.get("tools_used", []),
                "tool_output": state.get("tool_output", {}),
                "citations": state.get("citations", []),
                "approval_status": state.get("approval_status", "not_required"),
                "requires_approval": state.get("requires_approval", False),
                "thread_id": thread_id,
                "history": state.get("history", []),
            }
        
        except Exception as e:
            return {
                "question": question,
                "answer": f"Fallback execution error: {str(e)}",
                "tools_used": [],
                "tool_output": {},
                "citations": [],
                "approval_status": "error",
                "requires_approval": False,
                "thread_id": thread_id,
                "history": history,
                "error": str(e),
            }


if __name__ == "__main__":
    """Test LangGraph agent with sample questions."""
    
    print("=" * 70)
    print("LangGraph Agent Test")
    print(f"LangGraph Available: {LANGGRAPH_AVAILABLE}")
    print("=" * 70)
    print()
    
    test_questions = [
        ("How much subsidy for 3 kW?", True),
        ("I want 4 kW on my house", False),  # Should trigger approval
        ("I want 4 kW on my house", True),   # With approval
    ]
    
    for question, approved in test_questions:
        print(f"\nQuestion: {question}")
        print(f"Approved: {approved}")
        print("-" * 70)
        
        result = run_graph_agent(
            question=question,
            thread_id="test_session",
            approved=approved
        )
        
        print(f"Tools Used: {', '.join(result['tools_used'])}")
        print(f"Approval Status: {result['approval_status']}")
        print(f"Citations: {len(result['citations'])}")
        print(f"\nAnswer Preview:")
        print(result['answer'][:300] + "...")
        
        print("\n" + "=" * 70)
    
    print("\nGraph agent test complete!")
