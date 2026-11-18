"""
Day 10 — SuryaGharSathi Streamlit UI
=====================================
Interactive chat interface with:
- Chat Assistant (POST /ask or POST /agent endpoints)
- Official MNRE citations display
- Thumbs up/down feedback persistence
- Signature Feature: Solar Payback Chart (2 kW vs 3 kW comparison)
- Mandatory safety disclaimer

Run with:
    streamlit run ui/app.py
"""

import streamlit as st
import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add parent directory to path for direct imports (fallback mode)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import for fallback mode
try:
    from app.rag import answer_question
    from app.graph import run_graph_agent
    from app.tools import solar_cfa_calculator
    FALLBACK_AVAILABLE = True
except ImportError:
    FALLBACK_AVAILABLE = False


# Page config
st.set_page_config(
    page_title="SuryaGharSathi - PM Surya Ghar Assistant",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .safety-note {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .citation-box {
        background-color: #F8F9FA;
        border-left: 3px solid #007BFF;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .metric-card {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .tool-badge {
        background-color: #E3F2FD;
        color: #1976D2;
        padding: 0.3rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.2rem;
    }
    .feedback-btn {
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "default"

if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = []


def save_feedback(question: str, answer: str, rating: str, timestamp: str):
    """Save feedback to data/feedback.jsonl"""
    feedback_entry = {
        "timestamp": timestamp,
        "question": question,
        "answer": answer[:200],  # First 200 chars
        "rating": rating,
        "thread_id": st.session_state.thread_id
    }
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Append to JSONL file
    with open("data/feedback.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_entry) + "\n")
    
    st.session_state.feedback_data.append(feedback_entry)


def call_api(endpoint: str, payload: Dict[str, Any], backend_url: str) -> Optional[Dict[str, Any]]:
    """Call FastAPI endpoint with fallback to direct function calls."""
    try:
        # Try API call first
        url = f"{backend_url}{endpoint}"
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    
    except Exception as api_error:
        # Fallback to direct function calls if API unavailable
        if FALLBACK_AVAILABLE:
            st.warning(f"⚠️ API unavailable, using direct fallback mode: {str(api_error)[:100]}")
            
            try:
                if endpoint == "/ask":
                    result = answer_question(
                        payload["question"],
                        top_k=payload.get("top_k", 4)
                    )
                    return {
                        "question": result["question"],
                        "answer": result["answer"],
                        "citations": result.get("citations", []),
                        "confidence": result.get("confidence", "medium"),
                    }
                
                elif endpoint == "/agent":
                    result = run_graph_agent(
                        question=payload["question"],
                        thread_id=payload.get("thread_id", "default"),
                        approved=payload.get("approved", True)
                    )
                    return result
                
            except Exception as fallback_error:
                st.error(f"❌ Fallback failed: {str(fallback_error)}")
                return None
        else:
            st.error(f"❌ API call failed and fallback not available: {str(api_error)}")
            return None


def display_citations(citations: List[Dict[str, Any]]):
    """Display citations in expandable section."""
    if not citations or len(citations) == 0:
        return
    
    with st.expander(f"📚 **Official MNRE Citations** ({len(citations)} sources)", expanded=False):
        for i, cite in enumerate(citations, 1):
            st.markdown(f"""
            <div class="citation-box">
                <strong>[{i}] {cite.get('title', 'Unknown')} </strong><br>
                📄 Page {cite.get('page', 'N/A')} | 
                📅 Issued: {cite.get('date_issued', 'N/A')} | 
                🎯 Relevance: {cite.get('score', 0):.2%}<br>
                <small>🔗 <a href="{cite.get('source', '#')}" target="_blank">Source Document</a></small>
            </div>
            """, unsafe_allow_html=True)


def display_feedback_buttons(msg_index: int, question: str, answer: str):
    """Display thumbs up/down feedback buttons."""
    col1, col2 = st.columns([1, 1])
    
    timestamp = datetime.now().isoformat()
    
    with col1:
        if st.button("👍 Helpful", key=f"helpful_{msg_index}", help="Mark this answer as helpful"):
            save_feedback(question, answer, "helpful", timestamp)
            st.success("✓ Feedback saved!")
    
    with col2:
        if st.button("👎 Not Helpful", key=f"not_helpful_{msg_index}", help="Mark this answer as not helpful"):
            save_feedback(question, answer, "not_helpful", timestamp)
            st.warning("Feedback saved. We'll improve!")


def calculate_payback_data(
    capacity_kw: float,
    monthly_bill: float,
    special_category: bool = False
) -> Dict[str, Any]:
    """Calculate year-by-year payback data."""
    try:
        calc_result = solar_cfa_calculator(
            capacity_kw=capacity_kw,
            special_category_state=special_category,
            monthly_bill_inr=monthly_bill
        )
        
        # Calculate yearly savings (70% bill offset assumption)
        annual_savings = monthly_bill * 12 * 0.70
        net_cost = calc_result['net_cost_inr']
        
        # Year-by-year cumulative data
        years = list(range(0, 16))
        cumulative_savings = [annual_savings * year for year in years]
        net_cost_line = [net_cost] * len(years)
        
        # Find payback year
        payback_year = None
        for year, savings in enumerate(cumulative_savings):
            if savings >= net_cost:
                payback_year = year
                break
        
        return {
            "calc_result": calc_result,
            "years": years,
            "cumulative_savings": cumulative_savings,
            "net_cost_line": net_cost_line,
            "payback_year": payback_year,
            "annual_savings": annual_savings,
        }
    
    except Exception as e:
        st.error(f"Calculation error: {str(e)}")
        return None


def plot_payback_chart(payback_data: Dict[str, Any], capacity_kw: float):
    """Generate interactive payback chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = payback_data["years"]
    cumulative_savings = payback_data["cumulative_savings"]
    net_cost_line = payback_data["net_cost_line"]
    payback_year = payback_data["payback_year"]
    
    # Plot lines
    ax.plot(years, cumulative_savings, 'g-', linewidth=2, label='Cumulative Electricity Savings')
    ax.plot(years, net_cost_line, 'r--', linewidth=2, label='Net System Cost (after CFA)')
    
    # Mark payback point
    if payback_year:
        ax.axvline(x=payback_year, color='orange', linestyle=':', linewidth=2, alpha=0.7)
        ax.plot(payback_year, net_cost_line[0], 'o', markersize=10, color='orange', 
                label=f'Break-Even at Year {payback_year}')
        ax.text(payback_year, net_cost_line[0] * 1.1, f'Payback: {payback_year} years', 
                ha='center', fontsize=10, fontweight='bold', color='orange')
    
    # Styling
    ax.set_xlabel('Years', fontsize=12, fontweight='bold')
    ax.set_ylabel('Amount (₹)', fontsize=12, fontweight='bold')
    ax.set_title(f'Rooftop Solar Payback Analysis — {capacity_kw} kW System', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Format y-axis as Indian currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    plt.tight_layout()
    
    return fig


# ============================================================================
# MAIN APP
# ============================================================================

# Header
st.markdown('<div class="main-header">☀️ SuryaGharSathi</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">PM Surya Ghar: Muft Bijli Yojana Assistant for Kopargaon Homeowners</div>', 
            unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Mode selector
    mode = st.radio(
        "Mode",
        options=["🤖 Agent (with Tools)", "💬 RAG Q&A"],
        index=0,
        help="Agent uses solar_cfa_calculator tool + RAG. RAG-only uses retrieval."
    )
    
    endpoint = "/agent" if "Agent" in mode else "/ask"
    
    # Backend URL
    backend_url = st.text_input(
        "FastAPI Backend URL",
        value="http://127.0.0.1:8000",
        help="URL of running FastAPI server. Falls back to direct calls if unavailable."
    )
    
    # Thread ID for memory
    st.session_state.thread_id = st.text_input(
        "Thread ID (for memory)",
        value=st.session_state.thread_id,
        help="Unique ID for multi-turn conversation memory"
    )
    
    # Approval checkbox
    approved = st.checkbox(
        "Approve >3 kW systems",
        value=True,
        help="Pre-approve systems >3 kW where CFA is capped at ₹78,000"
    )
    
    st.divider()
    
    # Sample questions (6 project card questions)
    st.subheader("💡 Quick Questions")
    
    sample_questions = [
        "How much subsidy for 3 kW?",
        "How much terrace area for 1 kW?",
        "What is the minimum warranty?",
        "I want 4 kW in Kopargaon. Do I need net metering?",
        "My vendor says pay first. How many days for subsidy?",
        "What will MSEDCL's tariff be next year?",  # Q6 - should abstain
    ]
    
    for i, q in enumerate(sample_questions):
        if st.button(q, key=f"sample_{i}"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
    
    st.divider()
    
    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Safety note in sidebar
    st.markdown("""
    <div class="safety-note">
        ⚠️ <strong>Important:</strong><br>
        Information from official MNRE sources, not financial advice. 
        Confirm final amounts with your DISCOM and the national portal 
        before paying a vendor.
    </div>
    """, unsafe_allow_html=True)

# Main tabs
tab1, tab2 = st.tabs(["💬 Chat Assistant", "📊 Solar Payback Calculator"])

# ============================================================================
# TAB 1: CHAT ASSISTANT
# ============================================================================
with tab1:
    st.subheader("Chat with SuryaGharSathi")
    
    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show tool badges if available
            if message["role"] == "assistant" and "tools_used" in message:
                st.markdown("**Tools Used:**")
                for tool in message["tools_used"]:
                    st.markdown(f'<span class="tool-badge">🔧 {tool}</span>', unsafe_allow_html=True)
            
            # Show citations if available
            if message["role"] == "assistant" and "citations" in message:
                display_citations(message["citations"])
            
            # Show feedback buttons for assistant messages
            if message["role"] == "assistant":
                display_feedback_buttons(i, 
                    st.session_state.messages[i-1]["content"] if i > 0 else "",
                    message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about PM Surya Ghar subsidies, requirements, or payback..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Call API and get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                payload = {
                    "question": prompt,
                }
                
                if endpoint == "/agent":
                    payload["thread_id"] = st.session_state.thread_id
                    payload["approved"] = approved
                else:
                    payload["top_k"] = 4
                
                result = call_api(endpoint, payload, backend_url)
                
                if result:
                    answer = result.get("answer", "No answer received.")
                    citations = result.get("citations", [])
                    tools_used = result.get("tools_used", [])
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Show tool badges
                    if tools_used:
                        st.markdown("**Tools Used:**")
                        for tool in tools_used:
                            st.markdown(f'<span class="tool-badge">🔧 {tool}</span>', unsafe_allow_html=True)
                    
                    # Show citations
                    display_citations(citations)
                    
                    # Store message with metadata
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "citations": citations,
                        "tools_used": tools_used,
                    })
                    
                    # Show feedback buttons
                    display_feedback_buttons(len(st.session_state.messages) - 1, prompt, answer)
                else:
                    error_msg = "Sorry, I couldn't process your request. Please check the backend connection."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "citations": [],
                        "tools_used": [],
                    })

# ============================================================================
# TAB 2: SOLAR PAYBACK CALCULATOR (SIGNATURE FEATURE)
# ============================================================================
with tab2:
    st.subheader("☀️ Interactive Solar Subsidy & Payback Calculator")
    st.markdown("**Calculate your rooftop solar system cost, CFA subsidy, and payback period**")
    
    # Input section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_bill = st.slider(
            "Monthly MSEDCL Bill (₹)",
            min_value=500,
            max_value=15000,
            value=2000,
            step=100,
            help="Your average monthly electricity bill"
        )
    
    with col2:
        system_size = st.slider(
            "System Size (kW)",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.5,
            help="Rooftop solar system capacity in kW"
        )
    
    with col3:
        available_area = st.number_input(
            "Available Terrace Area (sq m)",
            min_value=10,
            max_value=200,
            value=40,
            step=5,
            help="Shadow-free terrace area available for solar panels"
        )
    
    # State category
    state_category = st.radio(
        "State Category",
        options=["General State (Maharashtra)", "Special Category State"],
        index=0,
        horizontal=True
    )
    
    special_category = "Special" in state_category
    
    st.divider()
    
    # Calculate button
    if st.button("📊 Calculate Subsidy & Payback", type="primary"):
        with st.spinner("Calculating..."):
            payback_data = calculate_payback_data(system_size, monthly_bill, special_category)
            
            if payback_data:
                calc = payback_data["calc_result"]
                
                # Display KPI metrics
                st.markdown("### 💰 Financial Summary")
                
                metric_cols = st.columns(4)
                
                with metric_cols[0]:
                    st.metric(
                        label="Gross System Cost",
                        value=f"₹{calc['benchmark_cost_inr']:,.0f}",
                        help="MNRE benchmark cost before subsidy"
                    )
                
                with metric_cols[1]:
                    st.metric(
                        label="CFA Subsidy",
                        value=f"₹{calc['cfa_subsidy_inr']:,.0f}",
                        delta="Central Financial Assistance" if not calc['capped'] else "Capped at 3 kW",
                        help="Government subsidy amount"
                    )
                
                with metric_cols[2]:
                    st.metric(
                        label="Net Cost to You",
                        value=f"₹{calc['net_cost_inr']:,.0f}",
                        delta=f"-{(calc['cfa_subsidy_inr']/calc['benchmark_cost_inr']*100):.0f}%",
                        help="Cost after CFA subsidy"
                    )
                
                with metric_cols[3]:
                    if calc['estimated_payback_years']:
                        st.metric(
                            label="Payback Period",
                            value=f"{calc['estimated_payback_years']} years",
                            help="Time to recover net investment"
                        )
                    else:
                        st.metric(label="Payback Period", value="N/A")
                
                st.divider()
                
                # Roof area check
                required_area = calc['shadow_free_area_sq_m']
                area_ok = available_area >= required_area
                
                area_col1, area_col2 = st.columns([2, 1])
                
                with area_col1:
                    if area_ok:
                        st.success(f"✅ **Roof Area Check:** You have sufficient space! "
                                 f"Required: {required_area} sq m, Available: {available_area} sq m")
                    else:
                        st.error(f"❌ **Roof Area Check:** Insufficient space! "
                               f"Required: {required_area} sq m, Available: {available_area} sq m")
                        st.info(f"💡 Consider reducing system size to {(available_area / 10):.1f} kW")
                
                with area_col2:
                    if calc['capped']:
                        st.warning("⚠️ **CFA Capped:** No subsidy beyond 3 kW")
                
                st.divider()
                
                # Payback chart
                st.markdown("### 📈 Year-by-Year Payback Analysis")
                
                fig = plot_payback_chart(payback_data, system_size)
                st.pyplot(fig)
                
                st.caption(f"Assumptions: ₹{monthly_bill}/month electricity bill, 70% bill offset by solar, "
                         f"{system_size} kW system, {calc['state_category']} state rates")
                
                st.divider()
                
                # Comparison: 2 kW vs 3 kW for Kopargaon homeowner
                st.markdown("### 🏠 Side-by-Side Comparison: 2 kW vs 3 kW for Kopargaon Homeowner")
                st.markdown("*Target User: ₹2,000/month MSEDCL bill, 40 sq m terrace*")
                
                # Calculate 2 kW and 3 kW scenarios
                scenario_2kw = calculate_payback_data(2.0, 2000, False)
                scenario_3kw = calculate_payback_data(3.0, 2000, False)
                
                if scenario_2kw and scenario_3kw:
                    comp_col1, comp_col2 = st.columns(2)
                    
                    with comp_col1:
                        st.markdown("#### 2 kW System")
                        st.markdown(f"""
                        - **CFA Subsidy:** ₹{scenario_2kw['calc_result']['cfa_subsidy_inr']:,.0f}
                        - **Gross Cost:** ₹{scenario_2kw['calc_result']['benchmark_cost_inr']:,.0f}
                        - **Net Cost:** ₹{scenario_2kw['calc_result']['net_cost_inr']:,.0f}
                        - **Roof Area:** {scenario_2kw['calc_result']['shadow_free_area_sq_m']} sq m
                        - **Payback:** {scenario_2kw['payback_year']} years
                        - **Annual Savings:** ₹{scenario_2kw['annual_savings']:,.0f}
                        """)
                    
                    with comp_col2:
                        st.markdown("#### 3 kW System ⭐ Recommended")
                        st.markdown(f"""
                        - **CFA Subsidy:** ₹{scenario_3kw['calc_result']['cfa_subsidy_inr']:,.0f}
                        - **Gross Cost:** ₹{scenario_3kw['calc_result']['benchmark_cost_inr']:,.0f}
                        - **Net Cost:** ₹{scenario_3kw['calc_result']['net_cost_inr']:,.0f}
                        - **Roof Area:** {scenario_3kw['calc_result']['shadow_free_area_sq_m']} sq m
                        - **Payback:** {scenario_3kw['payback_year']} years
                        - **Annual Savings:** ₹{scenario_3kw['annual_savings']:,.0f}
                        """)
                    
                    st.info(f"💡 **Recommendation:** 3 kW system maximizes CFA subsidy (capped at ₹78,000) "
                           f"and provides {scenario_3kw['payback_year']} year payback with your ₹2,000/month bill.")
                
                st.divider()
                
                # Detailed breakdown table
                with st.expander("📋 Detailed CFA Calculation Breakdown"):
                    st.markdown("**Slab-Based CFA Calculation:**")
                    
                    for slab_name, slab_data in calc['slab_breakdown'].items():
                        if slab_data['capacity_kw'] > 0:
                            st.markdown(f"""
                            - **{slab_data['description']}:** 
                              {slab_data['capacity_kw']} kW × ₹{slab_data['rate_per_kw']:,}/kW = 
                              ₹{slab_data['cfa_amount']:,.0f}
                            """)
                    
                    st.markdown(f"**Total CFA:** ₹{calc['cfa_subsidy_inr']:,.0f}")
                    
                    if calc['capped']:
                        st.warning("⚠️ Subsidy capped at 3 kW. Additional capacity receives no CFA.")

# Footer
st.divider()
st.markdown("""
<div class="safety-note">
    <strong>⚠️ Important Safety & Disclaimer:</strong><br>
    This tool provides estimates based on official MNRE PM Surya Ghar: Muft Bijli Yojana guidelines. 
    Final subsidy amounts, system costs, and installation requirements must be confirmed with:
    <ul>
        <li>Your local DISCOM (MSEDCL for Maharashtra)</li>
        <li>National Portal: <a href="https://pmsuryaghar.gov.in" target="_blank">pmsuryaghar.gov.in</a></li>
        <li>Registered solar vendor from the national portal</li>
    </ul>
    This is informational guidance, not financial or legal advice. Always verify with official sources before making payment decisions.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <strong>SuryaGharSathi</strong> | Student: Abhishek Sanjay Dighe (2124UMLM2056) | 
    Project: SJ-64 | Built with FastAPI + LangGraph + Streamlit
</div>
""", unsafe_allow_html=True)
