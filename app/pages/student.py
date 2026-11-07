import streamlit as st
import plotly.express as px
from app.pages.common import hero
from src.services import get_student,get_student_records
from src.recommendations.risk import assess_risk,recommendations_for

def render_dashboard(user):
    sid=user.get("student_id")
    s=get_student(sid) if sid else None
    if not s:
        hero("Student dashboard","Your academic workspace.")
        st.warning("Your account is not linked to a student profile. Contact the administrator.")
        return
    records=get_student_records(sid)
    hero(f"Welcome, {s['name'].split()[0]} 👋","Your progress, learning indicators and suggested next steps.")
    if records.empty: st.info("No academic records yet."); return
    latest=records.iloc[-1].to_dict()
    risk,reasons=assess_risk(latest)
    a,b,c,d=st.columns(4)
    a.metric("CGPA",f"{s['previous_cgpa']:.2f}")
    b.metric("Attendance",f"{latest.get('Attendance',0):.1f}%")
    c.metric("Latest marks",f"{latest.get('Final_Marks',0):.1f}/100")
    d.metric("Support indicator",risk)
    st.subheader("Performance trend")
    st.plotly_chart(px.line(records,x="recorded_at",y="Final_Marks",markers=True,
                            labels={"recorded_at":"Recorded date","Final_Marks":"Final marks"}),use_container_width=True)
    st.subheader("Personalized recommendations")
    for tip in recommendations_for(latest): st.write("•",tip)
    with st.expander("Understand your support indicator"):
        for reason in reasons: st.write("•",reason)
    st.caption("Indicators and predictions support guidance only; they are estimates, not guarantees.")

def render_planner(user):
    hero("My study planner","Create a practical weekly plan and track your study tasks.")
    subjects=st.text_input("Subjects / topics (comma separated)","DBMS, Mathematics, Programming")
    hours=st.slider("Available study hours this week",2,35,10)
    goal=st.text_input("Learning goal","Improve my next assessment")
    topics=[x.strip() for x in subjects.split(",") if x.strip()]
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    if st.button("Build weekly plan",type="primary"):
        if topics:
            st.session_state.study_tasks=[{"day":d,"task":topics[i%len(topics)],"hours":round(hours/7,1),"done":False} for i,d in enumerate(days)]
            st.session_state.study_goal=goal
    if "study_tasks" in st.session_state:
        st.write(f"**Goal:** {st.session_state.get('study_goal','')}")
        for i,task in enumerate(st.session_state.study_tasks):
            task["done"]=st.checkbox(f"{task['day']} · {task['task']} — {task['hours']} hours",value=task["done"],key=f"task_{i}")
