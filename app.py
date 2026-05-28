import streamlit as st
import pdfplumber
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os




from datetime import datetime
from pathlib import Path
from utils.storage_manager import (
    load_history,
    save_to_history,
    load_comparisons,
    save_comparison,
    clear_all_data
)
from utils.pdf_extractor import extract_resume_text
from backend.ats.skill_extractor import extract_skills
from backend.ats.ats_engine import calculate_ats_score
from backend.recommender.recommender_engine import recommend_jobs, jobs_df
from backend.chatbot.chatbot_engine import chatbot_response

from backend.analytics.analytics_engine import (
    calculate_history_statistics,
    prepare_trend_data,
    compare_analyses
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Career Copilot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# DATA STORAGE & MANAGEMENT
# =========================================================

DATA_DIR = Path("career_copilot_data")
HISTORY_FILE = DATA_DIR / "history.json"
COMPARISONS_FILE = DATA_DIR / "comparisons.json"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

def load_history():
    """Load resume analysis history from local storage"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_to_history(analysis_data):
    """Save analysis data to history"""
    history = load_history()
    history.append(analysis_data)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def load_comparisons():
    """Load saved comparisons from local storage"""
    if COMPARISONS_FILE.exists():
        with open(COMPARISONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_comparison(comparison_name, comparison_data):
    """Save comparison data"""
    comparisons = load_comparisons()
    comparisons[comparison_name] = comparison_data
    with open(COMPARISONS_FILE, 'w') as f:
        json.dump(comparisons, f, indent=2)

def clear_all_data():
    """Clear all stored data"""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    if COMPARISONS_FILE.exists():
        COMPARISONS_FILE.unlink()

# Initialize session state
if 'show_history' not in st.session_state:
    st.session_state.show_history = False
if 'show_comparisons' not in st.session_state:
    st.session_state.show_comparisons = False
if 'selected_history_indices' not in st.session_state:
    st.session_state.selected_history_indices = []

# =========================================================
# CUSTOM CSS - LUXURY TECH AESTHETIC
# =========================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&family=Playfair+Display:wght@700;800&display=swap');

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1428 100%);
        color: #e8edf5;
        font-family: 'Sora', sans-serif;
        overflow-x: hidden;
    }

    .main {
        background: transparent;
        color: #e8edf5;
    }

    .block-container {
        padding-top: 3rem;
        padding-left: 4rem;
        padding-right: 4rem;
        max-width: 1600px;
        margin: 0 auto;
    }

    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.2);
        }
        50% {
            box-shadow: 0 0 40px rgba(0, 245, 255, 0.4);
        }
    }

    @keyframes shimmer {
        0% {
            left: -100%;
        }
        100% {
            left: 100%;
        }
    }

    @keyframes glow {
        0%, 100% {
            text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
        }
        50% {
            text-shadow: 0 0 20px rgba(0, 245, 255, 0.8);
        }
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* TYPOGRAPHY */
    h1 {
        font-family: 'Playfair Display', serif;
        color: #ffffff;
        text-align: center;
        font-size: 72px !important;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #00f5ff 0%, #0099ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeInUp 0.8s ease-out;
    }

    h2 {
        font-family: 'Sora', sans-serif;
        color: #ffffff;
        font-size: 28px !important;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
        animation: slideInLeft 0.6s ease-out;
    }

    h3 {
        font-family: 'Sora', sans-serif;
        color: #b8c5e0;
        font-size: 18px !important;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
        animation: slideInLeft 0.5s ease-out;
    }

    p {
        color: #c5d0e8;
        line-height: 1.6;
        font-size: 15px;
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.3), transparent);
        margin: 3rem 0;
        animation: fadeInUp 0.6s ease-out;
    }

    /* METRIC CARD */
    .metric-card {
        background: linear-gradient(135deg, rgba(15, 32, 65, 0.8) 0%, rgba(25, 40, 80, 0.8) 100%);
        padding: 32px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 
            0 8px 32px rgba(0, 245, 255, 0.1),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        margin-bottom: 24px;
        border: 1px solid rgba(0, 245, 255, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out forwards;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.1), transparent);
        transition: left 0.5s ease;
        pointer-events: none;
    }

    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 
            0 16px 48px rgba(0, 245, 255, 0.2),
            inset 0 1px 1px rgba(255, 255, 255, 0.15);
        border-color: rgba(0, 245, 255, 0.3);
        animation: pulse 1.5s ease-in-out infinite;
    }

    .metric-card:hover::before {
        left: 100%;
    }

    .metric-card h2 {
        background: linear-gradient(135deg, #00f5ff 0%, #0099ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }

    .metric-card h1 {
        font-size: 48px !important;
        margin: 12px 0 0 0;
        letter-spacing: 0;
    }

    /* SKILL BOX */
    .skill-box {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.08) 0%, rgba(0, 153, 255, 0.08) 100%);
        padding: 10px 16px;
        border-radius: 12px;
        margin: 6px;
        display: inline-block;
        color: #00f5ff;
        font-weight: 600;
        font-size: 13px;
        border: 1.5px solid rgba(0, 245, 255, 0.3);
        transition: all 0.3s ease;
        cursor: default;
        letter-spacing: 0.3px;
        text-transform: capitalize;
        animation: slideInLeft 0.5s ease-out;
    }

    .skill-box:hover {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.15) 0%, rgba(0, 153, 255, 0.15) 100%);
        border-color: rgba(0, 245, 255, 0.6);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 20px rgba(0, 245, 255, 0.2);
    }

    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00f5ff 0%, #0099ff 100%) !important;
        border-radius: 10px !important;
        animation: slideInLeft 0.8s ease-out;
    }

    .stProgress > div {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        height: 8px !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%);
        border-right: 1px solid rgba(0, 245, 255, 0.1);
        animation: slideInLeft 0.6s ease-out;
    }

    [data-testid="stSidebar"] > div > div {
        padding: 2rem 1.5rem !important;
    }

    /* SIDEBAR TITLE */
    [data-testid="stSidebar"] h1 {
        font-size: 24px !important;
        margin-bottom: 1.5rem;
        animation: slideInLeft 0.6s ease-out;
    }

    /* INFO BOX */
    [data-testid="stSidebarContent"] > .stInfo {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.08) 0%, rgba(0, 153, 255, 0.08) 100%);
        border-left: 3px solid #00f5ff !important;
        border-radius: 8px;
        padding: 16px !important;
        color: #c5d0e8;
        animation: slideInRight 0.6s ease-out;
    }

    [data-testid="stSidebarContent"] > .stSuccess {
        background: linear-gradient(135deg, rgba(0, 200, 150, 0.08) 0%, rgba(0, 150, 100, 0.08) 100%);
        border-left: 3px solid #00c896 !important;
        border-radius: 8px;
        padding: 12px !important;
        animation: slideInRight 0.6s ease-out;
    }

    /* FILE UPLOADER */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed rgba(0, 245, 255, 0.3) !important;
        background-color: rgba(0, 245, 255, 0.02) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }

    [data-testid="stFileUploadDropzone"]:hover {
        border-color: rgba(0, 245, 255, 0.6) !important;
        background-color: rgba(0, 245, 255, 0.05) !important;
        animation: pulse 1s ease-in-out infinite;
    }

    /* COLUMNS & LAYOUT */
    [data-testid="column"] {
        gap: 2rem;
    }

    /* PLOTLY CHARTS */
    .plotly-graph-div {
        background: transparent !important;
        animation: fadeInUp 0.8s ease-out;
    }

    .js-plotly-plot .plotly {
        background: transparent !important;
    }

    /* DIVIDER */
    .stDivider {
        background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.3), transparent);
    }

    /* SUBTLE GRAIN TEXTURE */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" result="noise"/></filter><rect width="100%" height="100%" filter="url(%23noise)" opacity="0.03"/></svg>');
        z-index: -1;
    }

    /* METRIC COUNTER STYLE */
    [data-testid="stMetricValue"] {
        font-family: 'Space Mono', monospace;
        font-size: 36px !important;
        font-weight: 700;
        background: linear-gradient(135deg, #00f5ff 0%, #0099ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: glow 2s ease-in-out infinite;
    }

    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #b8c5e0 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    /* BUTTON STYLE */
    button {
        background: linear-gradient(135deg, #0099ff 0%, #00f5ff 100%);
        border: none;
        color: #0a0e27;
        font-weight: 700;
        padding: 12px 28px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Sora', sans-serif;
        letter-spacing: 0.5px;
        animation: slideInLeft 0.5s ease-out;
    }

    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(0, 245, 255, 0.3);
        animation: pulse 0.6s ease-in-out;
    }

    button:active {
        transform: translateY(0);
    }

    /* HISTORY CARD */
    .history-card {
        background: linear-gradient(135deg, rgba(15, 32, 65, 0.6) 0%, rgba(25, 40, 80, 0.6) 100%);
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        transition: all 0.3s ease;
        animation: slideInRight 0.5s ease-out;
        cursor: pointer;
    }

    .history-card:hover {
        background: linear-gradient(135deg, rgba(15, 32, 65, 0.9) 0%, rgba(25, 40, 80, 0.9) 100%);
        border-color: rgba(0, 245, 255, 0.5);
        transform: translateX(5px);
        box-shadow: 0 8px 24px rgba(0, 245, 255, 0.15);
    }

    /* COMPARISON BADGE */
    .comparison-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(0, 200, 150, 0.2) 0%, rgba(0, 150, 100, 0.2) 100%);
        border: 1px solid rgba(0, 200, 150, 0.5);
        padding: 6px 12px;
        border-radius: 20px;
        color: #00c896;
        font-weight: 600;
        font-size: 12px;
        animation: slideDown 0.5s ease-out;
    }

    /* TAB STYLE */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid rgba(0, 245, 255, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        color: #b8c5e0;
        background: transparent;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.1) 0%, rgba(0, 153, 255, 0.1) 100%);
        border-bottom-color: #00f5ff !important;
        color: #00f5ff;
    }

    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.15) 0%, rgba(0, 153, 255, 0.15) 100%);
    }

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🚀 Career Copilot")

st.sidebar.markdown("""
---
""")

st.sidebar.markdown("""
### ✨ Features

📊 **Resume Analysis**  
Intelligent skill extraction from your resume

⭐ **ATS Score**  
Get insights on applicant tracking system compatibility

🎯 **Job Matching**  
Personalized job recommendations based on your skills

🔍 **Skill Gap Analysis**  
Identify missing skills for your target role

🛣️ **Career Roadmap**  
Step-by-step learning path to your dream job

📈 **Advanced Analytics**  
Beautiful visualizations of your career profile
""")

st.sidebar.markdown("---")

# History and Comparisons Section
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📜 History", use_container_width=True):
        st.session_state.show_history = not st.session_state.show_history

with col2:
    if st.button("📊 Compare", use_container_width=True):
        st.session_state.show_comparisons = not st.session_state.show_comparisons

st.sidebar.markdown("---")

# History Display
if st.session_state.show_history:
    st.sidebar.markdown("### 📜 Analysis History")
    history = load_history()
    
    if history:
        for idx, item in enumerate(reversed(history)):
            date_str = item.get('timestamp', 'Unknown date')
            ats_score = item.get('ats_score', 'N/A')
            
            st.sidebar.markdown(f"""
            <div class="history-card">
                <strong>Analysis #{len(history) - idx}</strong><br/>
                📅 {date_str}<br/>
                ⭐ ATS: {ats_score}/100<br/>
                🔧 Skills: {len(item.get('found_skills', []))}
            </div>
            """, unsafe_allow_html=True)
        
        if st.sidebar.button("🗑️ Clear History", use_container_width=True):
            history = []
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history, f)
            st.sidebar.success("History cleared!")
            st.rerun()
    else:
        st.sidebar.info("No analysis history yet. Upload a resume to start!")

st.sidebar.markdown("---")

st.sidebar.success("✅ Desktop Dashboard Ready")
st.sidebar.info("💡 Upload a PDF resume to get started!")

st.sidebar.markdown("""
---
**Version:** 2.0 Pro  
**Built with:** AI + ML + Local Storage
""")



# =========================================================
# TITLE & HEADER
# =========================================================

st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1>🚀 Career Copilot</h1>
    <p style="font-size: 18px; color: #b8c5e0; margin-top: 1rem; letter-spacing: 0.5px;">
        Your AI-Powered Career Intelligence Platform
    </p>
    <p style="font-size: 14px; color: #8a96b8; margin-top: 0.5rem;">
        Unlock opportunities • Analyze skills • Build your future
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# =========================================================
# FILE UPLOAD SECTION
# =========================================================

st.markdown("""
<div style="padding: 2rem 0;">
    <h2 style="margin-bottom: 1rem;">📄 Upload Your Resume</h2>
    <p style="color: #c5d0e8; margin-bottom: 1.5rem;">
        Share your resume in PDF format and let our AI analyze your career profile
    </p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    label_visibility="collapsed"
)

# =========================================================
# MAIN APP
# =========================================================

if uploaded_file is not None:

    # =====================================================
    # EXTRACT TEXT
    # =====================================================
    
    resume_text, total_pages = extract_resume_text(uploaded_file)

    # =====================================================
    # SKILL EXTRACTION
    # =====================================================

    found_skills = extract_skills(resume_text)

    ats_score = calculate_ats_score(found_skills)

    # =====================================================
    # AUTO SAVE TO HISTORY
    # =====================================================

    analysis_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ats_score": ats_score,
        "skills_count": len(found_skills),
        "found_skills": found_skills,
        "resume_pages": 0  # Will be updated with actual count
    }

    # =====================================================
    # DASHBOARD OVERVIEW
    # =====================================================

    st.markdown("""
    <h2 style="margin-top: 2rem; margin-bottom: 1.5rem;">📊 Analysis Overview</h2>
    """, unsafe_allow_html=True)

    # Save button and history info
    save_col1, save_col2, save_col3 = st.columns([2, 1, 1])
    
    with save_col1:
        pass
    
    with save_col2:
        if st.button("💾 Save Analysis", use_container_width=True, key="save_analysis"):
            save_to_history(analysis_data)
            st.success("✅ Analysis saved to history!")
    
    with save_col3:
        history_count = len(load_history())
        st.info(f"📊 {history_count} analyses saved")

    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        st.metric(
            label="ATS Score",
            value=f"{ats_score}",
            delta="Out of 100",
            delta_color="off"
        )

    with col2:
        st.metric(
            label="Skills Found",
            value=len(found_skills),
            delta="Extracted",
            delta_color="off"
        )

    with col3:
        st.metric(
            label="Recommended Jobs",
            value="3",
            delta="Top matches",
            delta_color="off"
        )

    with col4:
        st.metric(
            label="Resume Pages",
            value=total_pages,
            delta="Analyzed",
            delta_color="off"
        )

    # Update analysis data with actual page count
    analysis_data["resume_pages"] = total_pages

    st.markdown("---")

    # =====================================================
    # MAIN CONTENT LAYOUT
    # =====================================================

    left_col, right_col = st.columns([1.1, 1], gap="large")

    # =====================================================
    # LEFT COLUMN - SKILLS & ATS
    # =====================================================

    with left_col:

        st.markdown("""
        <h2 style="margin-bottom: 1.5rem;">✨ Your Skills</h2>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="padding: 1rem; background: linear-gradient(135deg, rgba(0, 245, 255, 0.05) 0%, rgba(0, 153, 255, 0.05) 100%); border-radius: 12px; border: 1px solid rgba(0, 245, 255, 0.1); margin-bottom: 2rem;">
        """, unsafe_allow_html=True)

        for skill in found_skills:
            st.markdown(
                f"<span class='skill-box'>{skill}</span>",
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # =================================================
        # ATS SCORE CARD
        # =================================================

        st.markdown("""
        <h2 style="margin-top: 2rem; margin-bottom: 1.5rem;">🎯 ATS Score</h2>
        """, unsafe_allow_html=True)

        st.progress(ats_score / 100)

        st.markdown(f"""
        <div class="metric-card">
            <h2>Applicant Tracking Score</h2>
            <h1>{ats_score}</h1>
            <p style="color: #8a96b8; margin-top: 0.5rem;">
                {('Excellent match!' if ats_score >= 80 else 'Good potential!' if ats_score >= 60 else 'Room for improvement')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # =================================================
        # SKILLS PIE CHART
        # =================================================

        st.markdown("""
        <h2 style="margin-top: 2rem; margin-bottom: 1rem;">📈 Skills Distribution</h2>
        """, unsafe_allow_html=True)

        skills_df = pd.DataFrame({
            "Skills": found_skills,
            "Count": [1] * len(found_skills)
        })

        fig = px.pie(
            skills_df,
            names="Skills",
            values="Count",
            title=None,
            hole=0.4
        )

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8edf5', family='Sora'),
            margin=dict(t=0, b=0, l=0, r=0),
            height=400
        )

        fig.update_traces(
            marker=dict(
                line=dict(color='rgba(10, 14, 39, 1)', width=2)
            ),
            textfont=dict(size=12)
        )

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # RIGHT COLUMN - JOB RECOMMENDATIONS
    # =====================================================

    with right_col:

        # =================================================
        # JOB RECOMMENDATION SECTION
        # =================================================

        st.markdown("""
        <h2 style="margin-bottom: 1.5rem;">💼 Recommended Jobs</h2>
        """, unsafe_allow_html=True)

        recommended_jobs, top_jobs = recommend_jobs(found_skills)

        for index, row in top_jobs.iterrows():
            match_pct = row['Match %']
            
            color = "#00c896" if match_pct >= 80 else "#00d4ff" if match_pct >= 60 else "#ffa500"

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba({int(0)}, {int(212)}, {int(255)}, 0.08) 0%, rgba({int(0)}, {int(153)}, {int(255)}, 0.08) 100%); 
                        padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(0, 245, 255, 0.2);
                        margin-bottom: 1.5rem; transition: all 0.3s ease;">
                <h3 style="margin: 0 0 0.5rem 0; color: #ffffff;">{row["Job Role"]}</h3>
                <p style="color: #8a96b8; margin: 0.5rem 0; font-size: 13px;">Match Score</p>
                <h2 style="margin: 0.5rem 0 0 0; background: linear-gradient(135deg, #00f5ff 0%, #0099ff 100%);
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                    {match_pct:.1f}%
                </h2>
            </div>
            """, unsafe_allow_html=True)

            st.progress(min(match_pct / 100, 1.0))

        # =================================================
        # TOP JOBS BAR CHART
        # =================================================

        st.markdown("""
        <h2 style="margin-top: 2rem; margin-bottom: 1rem;">🏆 Top Opportunities</h2>
        """, unsafe_allow_html=True)

        fig2 = px.bar(
            recommended_jobs.head(5),
            x="Job Role",
            y="Match %",
            color="Match %",
            color_continuous_scale=["#ff6b6b", "#ffa500", "#00d4ff", "#00c896"],
            title=None
        )

        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8edf5', family='Sora'),
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0, 245, 255, 0.1)'),
            margin=dict(t=0, b=0, l=0, r=0),
            height=350,
            hovermode='closest'
        )

        fig2.update_traces(
            marker=dict(
                line=dict(color='rgba(10, 14, 39, 1)', width=0)
            ),
            hovertemplate='<b>%{x}</b><br>Match: %{y:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # SKILL GAP ANALYSIS SECTION
    # =====================================================

    st.markdown("""
    <h2 style="margin-top: 2rem; margin-bottom: 1.5rem;">🎯 Skill Gap Analysis</h2>
    <p style="color: #c5d0e8; margin-bottom: 2rem;">
        Below is your readiness for the top recommended role
    </p>
    """, unsafe_allow_html=True)

    target_job = top_jobs.iloc[0]["Job Role"]

    job_row = jobs_df[
        jobs_df["Job Role"] == target_job
    ]

    job_skills_text = job_row.iloc[0]["Skills"]

    target_skills = set()

    for skill in skill:

        if skill.lower() in job_skills_text.lower():
            target_skills.add(skill)

    user_skill_set = set(found_skills)

    missing_skills = target_skills - user_skill_set

    career_readiness = 100 - (
        (len(missing_skills) / len(target_skills)) * 100
    )

    readiness_col1, readiness_col2 = st.columns([1, 1], gap="large")

    with readiness_col1:

        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #b8c5e0;">Career Readiness for</h3>
            <h2 style="margin: 0.5rem 0; color: #ffffff;">{}</h2>
            <h1 style="background: linear-gradient(135deg, #00f5ff 0%, #0099ff 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                       background-clip: text; margin: 1rem 0;">{:.1f}%</h1>
            <p style="color: #8a96b8; margin-top: 1rem; font-size: 13px;">
                {} 
            </p>
        </div>
        """.format(
            target_job,
            career_readiness,
            'Ready to apply! 🚀' if career_readiness >= 80 else 
            'Almost there! 💪' if career_readiness >= 60 else 
            'Keep learning! 📚'
        ), unsafe_allow_html=True)

        st.progress(career_readiness / 100)

    with readiness_col2:

        st.markdown("""
        <h3>📋 Missing Skills</h3>
        """, unsafe_allow_html=True)

        if len(missing_skills) == 0:

            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(0, 200, 150, 0.15) 0%, rgba(0, 150, 100, 0.15) 100%);
                        padding: 2rem; border-radius: 12px; border: 1px solid rgba(0, 200, 150, 0.3);
                        text-align: center;">
                <h3 style="color: #00c896; margin: 0;">✨ Perfect Match!</h3>
                <p style="color: #c5d0e8; margin: 0.5rem 0 0 0;">
                    Your resume matches all required skills
                </p>
            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(255, 165, 0, 0.08) 0%, rgba(255, 140, 0, 0.08) 100%);
                        padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 165, 0, 0.2);">
            """, unsafe_allow_html=True)

            for skill in sorted(missing_skills):
                st.markdown(f"""
                <div style="padding: 0.5rem 0; color: #ffa500; font-weight: 600;">
                    ◻ {skill}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # =====================================================
    # CAREER ROADMAP SECTION
    # =====================================================

    st.markdown("""
    <h2 style="margin-bottom: 1.5rem;">🛣️ Your Learning Roadmap</h2>
    <p style="color: #c5d0e8; margin-bottom: 2rem;">
        Follow these steps to achieve your career goal
    </p>
    """, unsafe_allow_html=True)

    if len(missing_skills) == 0:

        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(0, 200, 150, 0.15) 0%, rgba(0, 150, 100, 0.15) 100%);
                    padding: 2.5rem; border-radius: 12px; border: 1px solid rgba(0, 200, 150, 0.3);
                    text-align: center;">
            <h2 style="color: #00c896; margin: 0;">🎉 Ready to Apply!</h2>
            <p style="color: #c5d0e8; margin: 1rem 0 0 0; font-size: 15px;">
                You have all the skills needed for this role. Start applying today!
            </p>
        </div>
        """, unsafe_allow_html=True)

    else:

        missing_skills_list = sorted(list(missing_skills))
        
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
        """, unsafe_allow_html=True)

        for idx, skill in enumerate(missing_skills_list, 1):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(0, 245, 255, 0.08) 0%, rgba(0, 153, 255, 0.08) 100%);
                        padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(0, 245, 255, 0.2);
                        text-align: center; transition: all 0.3s ease;">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #00f5ff 0%, #0099ff 100%);
                           border-radius: 50%; display: flex; align-items: center; justify-content: center;
                           margin: 0 auto 1rem; color: #0a0e27; font-weight: 700; font-size: 18px;">
                    {idx}
                </div>
                <h3 style="margin: 0 0 0.5rem 0; color: #ffffff; font-size: 16px;">Learn</h3>
                <p style="color: #00f5ff; margin: 0; font-weight: 600; font-size: 14px;">
                    {skill.title()}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0, 200, 150, 0.1) 0%, rgba(0, 150, 100, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(0, 200, 150, 0.2);
                    margin-top: 2rem; text-align: center;">
            <p style="color: #c5d0e8; margin: 0; font-size: 14px;">
                📖 Estimated Learning Time: <strong>{len(missing_skills) * 2}-{len(missing_skills) * 4} weeks</strong> of consistent practice
            </p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# HISTORY & COMPARISON ANALYTICS SECTION
# =========================================================

st.markdown("---")

history_tab, comparison_tab = st.tabs(["📜 Analysis History", "📊 Progress Comparison"])

with history_tab:
    st.markdown("""
    <h2 style="margin-bottom: 1.5rem;">📜 Your Analysis History</h2>
    """, unsafe_allow_html=True)
    
    history = load_history()
    
    if history:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**All Analyses**")
        with col2:
            st.markdown("**ATS Score**")
        with col3:
            st.markdown("**Skills**")
        
        st.divider()
        
        for idx, item in enumerate(reversed(history), 1):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="history-card">
                    <strong>Analysis #{len(history) - idx + 1}</strong><br/>
                    <small>📅 {item.get('timestamp', 'Unknown')}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                score = item.get('ats_score', 'N/A')
                color = "#00c896" if score >= 80 else "#00d4ff" if score >= 60 else "#ffa500"
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>{score}/100</span>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<span style='color: #00f5ff;'>{item.get('skills_count', 0)} skills</span>", unsafe_allow_html=True)
        
        # Statistics Summary
        st.markdown("---")
        st.markdown("""
        <h3>📈 History Statistics</h3>
        """, unsafe_allow_html=True)
        
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

        stats = calculate_history_statistics(history)

    with stats_col1:
        st.metric(
            "Total Analyses",
            stats["total_analyses"]
        )

    with stats_col2:
        st.metric(
            "Avg ATS Score",
            f"{stats['avg_ats']:.1f}"
        )

    with stats_col3:
        st.metric(
            "Best ATS Score",
            stats["max_ats"]
        )

    with stats_col4:
        st.metric(
            "Total Skills Found",
            stats["total_skills"]
        )
            
      
        
        # Trend Chart
        if stats["total_analyses"] > 1:
            st.markdown("---")
            st.markdown("""
            <h3>📊 ATS Score Trend</h3>
            """, unsafe_allow_html=True)


            trend_data = prepare_trend_data(history)
            
    
            fig_trend = px.line(
                trend_data,
                x='Analysis',
                y='ATS Score',
                title=None,
                markers=True,
                line_shape='spline'
            )
            
            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8edf5', family='Sora'),
                showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(0, 245, 255, 0.1)', range=[0, 100]),
                hovermode='closest',
                height=300
            )
            
            fig_trend.update_traces(
                line=dict(color='#00f5ff', width=3),
                marker=dict(size=8, color='#0099ff'),
                hovertemplate='<b>%{x}</b><br>ATS Score: %{y:.0f}<extra></extra>'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        if st.button("🗑️ Clear All History", key="clear_hist"):
            clear_all_data()
            st.success("All history cleared!")
            st.rerun()
    
        else:
            st.info("💡 No analysis history yet. Upload a resume to start tracking your progress!")

with comparison_tab:
    st.markdown("""
    <h2 style="margin-bottom: 1.5rem;">📊 Compare Your Progress</h2>
    """, unsafe_allow_html=True)
    
    history = load_history()
    
    if len(history) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            idx1 = st.selectbox(
                "Select First Analysis",
                options=range(len(history)),
                format_func=lambda x: f"#{x+1} - {history[x].get('timestamp', 'Unknown')}"
            )
        
        with col2:
            idx2 = st.selectbox(
                "Select Second Analysis",
                options=range(len(history)),
                format_func=lambda x: f"#{x+1} - {history[x].get('timestamp', 'Unknown')}",
                index=len(history)-1
            )
        
        if idx1 != idx2:
            analysis1 = history[idx1]
            analysis2 = history[idx2]
            
            st.markdown("---")
            st.markdown("""
            <h3>🔍 Comparison Results</h3>
            """, unsafe_allow_html=True)
            
            comp_col1, comp_col2, comp_col3 = st.columns(3)
            
            with comp_col1:
                comparison_data = compare_analyses(
    analysis1,
    analysis2
)
                
         
            
            fig_comp = px.bar(
                comparison_data["comparison_df"],
                x='Analysis',
                y=['ATS Score', 'Skills'],
                title=None,
                barmode='group'
            )
            
            fig_comp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8edf5', family='Sora'),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(0, 245, 255, 0.1)'),
                hovermode='closest',
                height=400
            )
            
            fig_comp.update_traces(
                marker=dict(line=dict(color='rgba(10, 14, 39, 1)', width=0))
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
        
        else:
            st.warning("Please select two different analyses to compare.")
    
    else:
        st.info("💡 You need at least 2 saved analyses to compare. Upload and save multiple resumes to see progress!")



# =========================================================
# AI CAREER CHATBOT
# =========================================================

st.markdown("---")

st.markdown("""
<h2 style="margin-top: 2rem; margin-bottom: 1.5rem;">
🤖 AI Career Assistant
</h2>
<p style="color: #c5d0e8; margin-bottom: 2rem;">
Ask career questions and get AI-powered guidance
</p>
""", unsafe_allow_html=True)

# Chat Input
user_question = st.text_input(
    "💬 Ask about resume, ATS, skills, AI careers, projects, roadmap..."
)

# Chat Response Logic
if user_question:
    response = chatbot_response(user_question)

    response = response.replace("<p>", "")
    response = response.replace("</p>", "")
    response = response.replace("<br>", "")
    response = response.replace("<div>", "")
    response = response.replace("</div>", "")
    response = response.replace("```", "")

    # =====================================================
    # DISPLAY RESPONSE INSIDE BOX
    # =====================================================

    st.markdown(f"""
    <div class="metric-card">

    <h3 style="
    color:#00f5ff;
    text-align:center;
    margin-bottom:20px;
    ">
    🤖 AI ASSISTANT RESPONSE
    </h3>

    <div style="
    font-size:18px;
    line-height:2;
    color:#e8edf5;
    padding:20px;
    text-align:left;
    white-space: pre-line;
    ">
    {response}
    </div>

    </div>
    """, unsafe_allow_html=True)

    
                                    