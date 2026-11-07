import streamlit as st
from app.pages.common import hero
from src.services import get_students,get_student_records,get_student
from reports.report_generator import create_student_pdf

def render(user,student_only=False):
    hero("Academic reports","Generate a downloadable student and semester performance summary.")
    if student_only:
        sid=user.get("student_id")
        if not sid: st.warning("No linked student profile."); return
    else:
        students=get_students()
        if students.empty: st.info("No student records."); return
        sid=st.selectbox("Select student",students.student_id.tolist())
    s=get_student(sid); records=get_student_records(sid)
    if s:
        st.write(f"**{s['name']}** · {s['student_id']} · {s['department']} · Semester {s['semester']}")
    if st.button("Generate PDF report",type="primary"):
        pdf=create_student_pdf(s,records)
        st.download_button("Download TREKVERSE report",pdf,file_name=f"TREKVERSE_{sid}_report.pdf",mime="application/pdf")
