import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="SAFE-INTERN | AI Risk Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from intake.input_router import route_input
from intake.intake_agent import run_intake
from agents.planner_agent import run_planner
from utils.risk_engine import calculate_risk
from utils.explanation_engine import generate_explanation
from utils.guardrails import apply_guardrails
from database.db_init import init_db
init_db()

# --------------------------------------------------
# CUSTOM CSS & STYLING
# --------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Modern Dark Theme - Vercel/shadcn inspired */
    :root {
        --bg-color: #0F172A; /* Slate 900 */
        --card-bg: #1E293B;  /* Slate 800 */
        --text-primary: #F1F5F9; /* Slate 100 */
        --text-secondary: #94A3B8; /* Slate 400 */
        --accent-primary: #3B82F6; /* Blue 500 */
        --border-color: #334155; /* Slate 700 */
        
        --risk-low: #10B981;   /* Emerald 500 */
        --risk-med: #F59E0B;   /* Amber 500 */
        --risk-high: #EF4444;  /* Red 500 */
    }

    .stApp {
        background-color: var(--bg-color);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    p, li, span, label {
        color: var(--text-secondary) !important;
    }

    /* Modern Card Style */
    .card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .card:hover {
        border-color: var(--accent-primary);
    }

    /* Primary Button */
    .stButton>button {
        width: 100%;
        background-color: var(--accent-primary);
        color: white !important;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #2563EB; /* Blue 600 */
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--accent-primary) !important;
        border-bottom-color: var(--accent-primary) !important;
    }
    
    /* Risk Badge */
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("🛡️ SAFE-INTERN")
    st.markdown("### AI-Powered Internship Safety")
    st.info(
        "This system uses a multi-agent AI architecture to analyze details "
        "and detect potential red flags in internship offers."
    )
    
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("1. **Intake**: AI parses your input.")
    st.markdown("2. **Analysis**: Specialized agents check company, payments, and behavior.")
    st.markdown("3. **Risk Engine**: Calculates a safety score.")
    st.markdown("4. **Advisor**: Provides clear, actionable advice.")
    
    st.markdown("---")
    st.caption("v2.0 | Powered by Gemini Pro")


# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------

col_title, col_logo = st.columns([3, 1])
with col_title:
    st.title("Internship Risk Analyzer")
    st.markdown("#### Verify opportunities before you commit. Fast, private, and AI-driven.")

st.markdown("---")

# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------

input_container = st.container()

# --------------------------------------------------
# INPUT SECTION (TABS)
# --------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)
input_container = st.container()

with input_container:
    tab1, tab2, tab3 = st.tabs(["📝 Text / Email", "📄 PDF Document", "🔗 Website URL"])
    
    text_input = None
    pdf_file = None
    url_input = None

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        text_input = st.text_area(
            "Internship Description",
            height=200,
            placeholder="Paste the job description, email, or message here...",
            label_visibility="collapsed"
        )

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload Offer Letter", type=["pdf"], label_visibility="collapsed")
        if pdf_file:
            pdf_file = pdf_file.read()

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        url_input = st.text_input("Internship Link", placeholder="https://example.com/internship", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Centered Action Button
    col_spacer_l, col_btn, col_spacer_r = st.columns([1, 2, 1])
    with col_btn:
        analyze = st.button("Analyze Risk", type="primary")

# --------------------------------------------------
# PROCESSING & RESULTS
# --------------------------------------------------

if analyze:
    try:
        progress_text = "Starting analysis engine..."
        my_bar = st.progress(0, text=progress_text)

        clean_text = route_input(
            text_input=text_input,
            pdf_file=pdf_file,
            url=url_input
        )
        my_bar.progress(20, text="Parsing and structuring data with Gemini...")

        intake_schema = run_intake(clean_text)
        my_bar.progress(40, text="Deploying analysis agents...")

        agent_results = run_planner(intake_schema)
        my_bar.progress(70, text="Calculating risk factors...")

        risk_result = calculate_risk(agent_results)
        my_bar.progress(85, text="Generating safety report...")

        explanation = generate_explanation(risk_result)
        safe_output = apply_guardrails(explanation)
        
        my_bar.progress(100, text="Analysis complete!")
        my_bar.empty()

        # --------------------------------------------------
        # DASHBOARD
        # --------------------------------------------------

        st.markdown("---")
        st.subheader("📊 Analysis Report")

        # Top Level Metrics
        m1, m2, m3 = st.columns(3)
        
        score = safe_output["risk_score"]
        category = safe_output["risk_category"]
        
        # Dynamic Coloring based on CSS variables
        if score < 30:
            score_color = "var(--risk-low)"
            badge_bg = "rgba(16, 185, 129, 0.2)"
            badge_text = "#10B981"
        elif score < 60:
            score_color = "var(--risk-med)"
            badge_bg = "rgba(245, 158, 11, 0.2)"
            badge_text = "#F59E0B"
        else:
            score_color = "var(--risk-high)"
            badge_bg = "rgba(239, 68, 68, 0.2)"
            badge_text = "#EF4444"

        with m1:
            st.markdown(
                f"""
                <div class="card" style="text-align: center;">
                    <h3 style="margin:0; font-size: 0.9rem; text-transform: uppercase;">Risk Score</h3>
                    <h1 style="margin:0; font-size: 4rem; color: {score_color}; line-height: 1.2;">
                        {score}<span style="font-size: 1.5rem; color: var(--text-secondary);">/100</span>
                    </h1>
                </div>
                """, unsafe_allow_html=True
            )
        
        with m2:
            st.markdown(
                f"""
                <div class="card" style="text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100%;">
                    <h3 style="margin:0; font-size: 0.9rem; text-transform: uppercase;">Risk Level</h3>
                    <div style="margin-top: 10px;">
                        <span class="risk-badge" style="background-color: {badge_bg}; color: {badge_text};">
                            {category}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

        with m3:
            agents_run = len(agent_results)
            st.markdown(
                f"""
                <div class="card" style="text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100%;">
                    <h3 style="margin:0; font-size: 0.9rem; text-transform: uppercase;">Agents Active</h3>
                    <h2 style="margin:0; margin-top: 5px; color: var(--text-primary);">{agents_run}</h2>
                    <p style="margin:0; font-size: 0.8rem;">Specialized Analyzers</p>
                </div>
                """, unsafe_allow_html=True
            )

        # Main Content Grid
        c1, c2 = st.columns([2, 1])

        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 🧠 Executive Summary")
            st.write(safe_output["summary"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🔎 Key Findings")
            
            if not safe_output["explanations"]:
                st.markdown("- ✅ **No specific risk indicators found.**")
            else:
                for item in safe_output["explanations"]:
                    if "risk" in item.lower() or "alert" in item.lower() or "caution" in item.lower():
                         st.markdown(f"- 🔴 {item}")
                    else:
                         st.markdown(f"- ℹ️ {item}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Recommendations Section
            if safe_output.get("recommendations"):
                st.markdown(
                    f"""
                    <div class="card" style="border-left: 4px solid {score_color};">
                        <h4 style="margin-top:0;">💡 Actionable Advice</h4>
                    """, unsafe_allow_html=True
                )
                for rec in safe_output["recommendations"]:
                    st.markdown(f"- {rec}")
                st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### 📌 Risk Breakdown")
            for agent, s in safe_output["breakdown"].items():
                st.markdown(f"**{agent.title()} Risk**")
                # Normalize relative to max agent score approx 30
                progress_val = min(s / 30.0, 1.0)
                st.progress(progress_val)
                st.caption(f"{s} points")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error("An error occurred during analysis.")
        st.exception(e)
