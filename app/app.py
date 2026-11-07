import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent

if str(APP_DIR) in sys.path:
    sys.path.remove(str(APP_DIR))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from database.database import init_db, seed_demo_data
from src.auth import authenticate
from src.services import log_event
from app.pages import admin, faculty, student, analytics, prediction, reports

st.set_page_config(page_title="TREKVERSE", page_icon="🎓", layout="wide")
init_db()
seed_demo_data()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.block-container{padding-top:1.4rem;max-width:1500px}
h1,h2,h3{font-family:'Manrope',sans-serif;letter-spacing:-.4px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#101d35,#1c3b60)}
[data-testid="stSidebar"] *{color:#eef5ff!important}
.hero{padding:1.5rem 1.7rem;border-radius:18px;color:white;background:linear-gradient(110deg,#142a4f,#285c83 62%,#367f88);margin-bottom:1.1rem}
.hero h1{color:white;margin:0;font-size:2.05rem}
.hero p{color:#d8e8f6;margin:.4rem 0 0}
div[data-testid="stMetric"]{background:white;border:1px solid #e7edf5;padding:13px 16px;border-radius:14px}
.stButton>button{border-radius:10px;font-weight:600}

.stButton > button {
    color: #ffffff !important;
    background-color: #17365D !important;
    border: 1px solid #17365D !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #244B78 !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

def login():
    st.markdown('<div class="hero"><h1>🎓 TREKVERSE</h1><p>Understand progress. Predict thoughtfully. Support every learner.</p></div>',unsafe_allow_html=True)
    _,col,_=st.columns([1,1.1,1])
    with col:
        st.subheader("Welcome to your academic workspace")
        with st.form("login"):
            username=st.text_input("Username")
            password=st.text_input("Password",type="password")
            go=st.form_submit_button("Sign in",type="primary",use_container_width=True)
        if go:
            user=authenticate(username.strip(),password)
            if user:
                st.session_state.user=user
                log_event(user["id"],"login","Successful login")
                st.rerun()
            st.error("Invalid username or password.")
        st.info("Demo: admin / Admin@123 · faculty / Faculty@123 · student / Student@123")

if "user" not in st.session_state or not st.session_state.user:
    login()
else:
    user=st.session_state.user
    role=user["role"]
    with st.sidebar:
        st.markdown("## 🎓 TREKVERSE")
        st.caption("ACADEMIC INTELLIGENCE")
        st.divider()
        st.write(f"**{user['full_name']}**")
        st.caption(role.title())
        choices={
            "admin":["Overview","Student directory","Analytics","Prediction & what-if","Reports","Data import & quality"],
            "faculty":["Overview","Student directory","Analytics","Prediction & what-if","Reports"],
            "student":["My dashboard","My study planner","My report"]
        }
        page=st.radio("NAVIGATION",choices[role])
        st.divider()
        st.caption("Academic support · Explainable AI")
        if st.button("Sign out",use_container_width=True):
            log_event(user["id"],"logout","Signed out")
            st.session_state.user=None
            st.rerun()

    if role=="admin":
        if page=="Overview": admin.render_overview(user)
        elif page=="Student directory": admin.render_directory(user)
        elif page=="Analytics": analytics.render(user)
        elif page=="Prediction & what-if": prediction.render(user)
        elif page=="Reports": reports.render(user)
        elif page=="Data import & quality": admin.render_import(user)
    elif role=="faculty":
        if page=="Overview": faculty.render_overview(user)
        elif page=="Student directory": faculty.render_directory(user)
        elif page=="Analytics": analytics.render(user)
        elif page=="Prediction & what-if": prediction.render(user)
        elif page=="Reports": reports.render(user)
    else:
        if page=="My dashboard": student.render_dashboard(user)
        elif page=="My study planner": student.render_planner(user)
        elif page=="My report": reports.render(user,student_only=True)
