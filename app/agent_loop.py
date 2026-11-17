"""
Day 9 S1 — Hand-Written ReAct Agent Loop
=========================================
Implements Thought → Action → Observation → Final Answer pattern.

Features:
- Calls solar_cfa_calculator for capacity/subsidy/area calculations
- Calls answer_question (RAG) for policy/guideline citations
- Combines tool outputs with RAG citations for grounded responses
- Records step-by-step reasoning trace

Run with:
    python -m app.agent_loop
"""

from typing import Dict, Any, List, Optional
import re

from app.tools import extract_capacity_kw, solar_cfa_calculator
from app.rag import answer_question


def _needs_calculator(question: str) -> bool:
    """Check if question requires CFA calculator tool."""
    q_lower = question.lower()
    
    # Keywords indicating calculation needed
    calc_keywords = [
        'subsidy', 'cfa', 'how much', 'cost', 'price',
        'area', 'terrace', 'roof', 'space', 'square',
        'payback', 'recover', 'return',
        'kw', 'kwp', 'kilowatt', 'capacity'
    ]
    
    return any(kw in q_lower for kw in calc_keywords)


def _needs_rag(question: str) -> bool:
    """Check if question requires RAG policy lookup."""
    q_lower = question.lower()
    
    # Keywords indicating policy/guideline lookup needed
    rag_keywords = [
        'guideline', 'rule', 'requirement', 'eligibility',
        'warranty', 'dcr', 'net metering', 'discom',
        'vendor', 'registration', 'process', 'procedure',
        'grievance', 'npia', 'resco', 'benchmark',
        'what is', 'what are', 'how does', 'can i',
        'allowed', 'permitted', 'mandatory'
    ]
    
    return any(kw in q_lower for kw in rag_keywords)


def run_agent_loop(
    question: str,
    max_steps: int = 3,
    special_category_state: bool = False,
    monthly_bill_inr: float = 2000.0
) -> Dict[str, Any]:
    """
    Run hand-written ReAct-style agent loop.
    
    Steps:
    1. Thought: Analyze what the question needs
    2. Action: Call appropriate tool(s) - calculator and/or RAG
    3. Observation: Record tool outputs
    4. Final Answer: Synthesize grounded response
    
    Args:
        question: User question
        max_steps: Maximum reasoning steps (default: 3)
        special_category_state: True for special category states
        monthly_bill_inr: Monthly electricity bill for payback estimation
    
    Returns:
        Dictionary with answer, tools_used, tool_output, citations, steps
    """
    steps = []
    tools_used = []
    tool_output = {}
    citations = []
    
    # Step 1: Thought - Analyze the question
    thought_1 = "Analyzing the user's question to determine required tools."
    
    needs_calc = _needs_calculator(question)
    needs_rag_lookup = _needs_rag(question)
    
    if needs_calc:
        thought_1 += " The question involves capacity/subsidy/cost calculation, so I need the solar_cfa_calculator tool."
    
    if needs_rag_lookup:
        thought_1 += " The question asks about policy/guidelines, so I need to retrieve official MNRE rules via RAG."
    
    if not needs_calc and not needs_rag_lookup:
        thought_1 += " This appears to be a general question that might require RAG for guideline lookup."
        needs_rag_lookup = True
    
    steps.append({
        "step": 1,
        "type": "thought",
        "content": thought_1,
    })
    
    # Step 2: Action - Execute tools
    action_2 = "Executing required tools: "
    
    # Action 2a: Calculator tool (if needed)
    if needs_calc:
        capacity = extract_capacity_kw(question)
        
        if capacity and capacity > 0:
            action_2 += f"solar_cfa_calculator(capacity_kw={capacity})"
            tools_used.append("solar_cfa_calculator")
            
            try:
                calc_result = solar_cfa_calculator(
                    capacity_kw=capacity,
                    special_category_state=special_category_state,
                    monthly_bill_inr=monthly_bill_inr
                )
                tool_output["solar_cfa_calculator"] = calc_result
                
                observation_calc = (
                    f"Calculator returned: CFA subsidy = ₹{calc_result['cfa_subsidy_inr']:,.0f}, "
                    f"Shadow-free area = {calc_result['shadow_free_area_sq_m']} sq m, "
                    f"Net cost = ₹{calc_result['net_cost_inr']:,.0f}, "
                    f"Payback = {calc_result['estimated_payback_years']} years"
                )
                
                if calc_result['capped']:
                    observation_calc += " (CFA capped at 3 kW)"
                
                steps.append({
                    "step": 2,
                    "type": "action",
                    "tool": "solar_cfa_calculator",
                    "input": {"capacity_kw": capacity},
                    "output": calc_result,
                })
                
            except Exception as e:
                observation_calc = f"Calculator error: {str(e)}"
                steps.append({
                    "step": 2,
                    "type": "action",
                    "tool": "solar_cfa_calculator",
                    "input": {"capacity_kw": capacity},
                    "error": str(e),
                })
        else:
            observation_calc = "Could not extract capacity from question, skipping calculator."
            steps.append({
                "step": 2,
                "type": "action",
                "tool": "solar_cfa_calculator",
                "skipped": "No capacity found in question",
            })
    else:
        observation_calc = ""
    
    # Action 2b: RAG tool (if needed)
    if needs_rag_lookup:
        if tools_used:
            action_2 += ", answer_question(RAG)"
        else:
            action_2 += "answer_question(RAG)"
        
        tools_used.append("answer_question")
        
        try:
            rag_result = answer_question(question, top_k=4)
            tool_output["answer_question"] = rag_result
            citations = rag_result.get("citations", [])
            
            observation_rag = (
                f"RAG returned: {len(citations)} citations. "
                f"Answer: {rag_result['answer'][:150]}..."
            )
            
            steps.append({
                "step": 2 if not needs_calc else 3,
                "type": "action",
                "tool": "answer_question",
                "input": {"question": question},
                "output": {
                    "answer": rag_result["answer"],
                    "citations_count": len(citations),
                    "confidence": rag_result.get("confidence", "medium"),
                },
            })
            
        except Exception as e:
            observation_rag = f"RAG error: {str(e)}"
            steps.append({
                "step": 2 if not needs_calc else 3,
                "type": "action",
                "tool": "answer_question",
                "input": {"question": question},
                "error": str(e),
            })
    else:
        observation_rag = ""
    
    # Step 3: Observation - Record what we learned
    observation_combined = ""
    if observation_calc:
        observation_combined += observation_calc
    if observation_rag:
        if observation_combined:
            observation_combined += " | "
        observation_combined += observation_rag
    
    if observation_combined:
        steps.append({
            "step": 3 if needs_calc and needs_rag_lookup else 2,
            "type": "observation",
            "content": observation_combined,
        })
    
    # Step 4: Final Answer - Synthesize response
    answer = _synthesize_answer(question, tool_output, citations)
    
    steps.append({
        "step": len(steps) + 1,
        "type": "final_answer",
        "content": answer,
    })
    
    return {
        "question": question,
        "answer": answer,
        "tools_used": tools_used,
        "tool_output": tool_output,
        "citations": citations,
        "steps": steps,
        "confidence": tool_output.get("answer_question", {}).get("confidence", "medium") if "answer_question" in tool_output else "high",
    }


def _synthesize_answer(
    question: str,
    tool_output: Dict[str, Any],
    citations: List[Dict[str, Any]]
) -> str:
    """
    Synthesize final answer from tool outputs and citations.
    
    Combines:
    - Calculator results (if available)
    - RAG answer (if available)
    - Citations in proper format
    """
    answer_parts = []
    
    # Add calculator results if available
    if "solar_cfa_calculator" in tool_output:
        calc = tool_output["solar_cfa_calculator"]
        
        answer_parts.append(
            f"For a {calc['capacity_kw']} kW rooftop solar system in {calc['state_category']} states:\n"
        )
        
        answer_parts.append(
            f"• **CFA Subsidy:** ₹{calc['cfa_subsidy_inr']:,.0f}"
        )
        
        if calc['capped']:
            answer_parts.append(" (capped at 3 kW, no additional CFA beyond 3 kW)")
        
        answer_parts.append(
            f"\n• **Shadow-free Roof Area Required:** {calc['shadow_free_area_sq_m']} sq m "
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
                f"\n• **Estimated Payback Period:** {calc['estimated_payback_years']} years "
                f"(assuming ₹{calc['monthly_bill_assumed']:,.0f}/month electricity bill)"
            )
        
        answer_parts.append("\n\n**CFA Calculation Breakdown:**\n")
        for slab_name, slab_data in calc['slab_breakdown'].items():
            if slab_data['capacity_kw'] > 0:
                answer_parts.append(
                    f"• {slab_data['description']}: {slab_data['capacity_kw']} kW × "
                    f"₹{slab_data['rate_per_kw']:,}/kW = ₹{slab_data['cfa_amount']:,.0f}\n"
                )
    
    # Add RAG answer if available
    if "answer_question" in tool_output:
        rag_answer = tool_output["answer_question"]["answer"]
        
        if answer_parts:
            answer_parts.append("\n\n**Additional Guidelines:**\n")
        
        answer_parts.append(rag_answer)
    
    # Add citations if available
    if citations and len(citations) > 0:
        answer_parts.append("\n\n**Sources:**\n")
        for i, cite in enumerate(citations[:3], 1):
            answer_parts.append(
                f"{i}. {cite['title']} (Page {cite['page']}, Date: {cite['date_issued']})\n"
            )
    
    # If no tools provided output, return a fallback
    if not answer_parts:
        return "I don't have enough information to answer this question. Please provide more details or ask about PM Surya Ghar CFA subsidy, system requirements, or guidelines."
    
    return "".join(answer_parts)


if __name__ == "__main__":
    """Test agent loop with sample questions."""
    
    print("=" * 70)
    print("ReAct Agent Loop Test")
    print("=" * 70)
    print()
    
    test_questions = [
        "How much subsidy will I get for a 3 kW rooftop solar system?",
        "I want 4 kW on my house in Kopargaon. How much subsidy do I get, and do I still need net metering from MSEDCL?",
        "What is the minimum warranty on solar panels under this scheme?",
    ]
    
    for q in test_questions:
        print(f"\nQuestion: {q}")
        print("-" * 70)
        
        result = run_agent_loop(q, max_steps=3)
        
        print(f"Tools Used: {', '.join(result['tools_used'])}")
        print(f"Citations: {len(result['citations'])}")
        print(f"\nReasoning Steps:")
        for step in result['steps']:
            print(f"  Step {step['step']} ({step['type']}): {step.get('content', step.get('tool', 'N/A'))[:80]}...")
        
        print(f"\nAnswer Preview:")
        print(result['answer'][:300] + "...")
        
        print("\n" + "=" * 70)
    
    print("\nAgent loop test complete!")
