import streamlit as st
import pandas as pd
from app.pages.common import hero,metric_row,student_table,student_detail
from src.services import get_dashboard_stats,log_event,add_academic_record
from src.preprocessing.validation import validate_dataframe

def render_overview(user):
    hero("Administrator overview","Institution-wide academic monitoring, data quality and system operations.")
    metric_row(get_dashboard_stats())
    st.subheader("Current student support queue")
    df=student_table()
    if not df.empty:
        st.dataframe(df[df["Risk"]!="Low"],use_container_width=True,hide_index=True)
    st.info("Use Data import & quality to load authorized CSV/XLSX records. All dashboard figures are calculated from the current database.")

def render_directory(user):
    hero("Student directory","Search student profiles and review academic indicators.")
    df=student_table()
    q=st.text_input("Search by ID, name or department")
    if q: df=df[df.astype(str).apply(lambda col:col.str.contains(q,case=False,na=False)).any(axis=1)]
    st.dataframe(df,use_container_width=True,hide_index=True)
    if not df.empty:
        sid=st.selectbox("Open student profile",df["Student ID"].tolist())
        student_detail(sid,user,allow_intervention=True)

def render_import(user):
    hero("Data import & quality","Validate institutional records before saving them.")
    st.write("Required: Student_ID, Attendance, Internal_Marks, Assignment_Marks, Quiz_Marks, Study_Hours, Previous_CGPA, Backlogs, Final_Marks.")
    uploaded=st.file_uploader("Upload CSV or Excel",type=["csv","xlsx"])
    if uploaded:
        try:
            df=pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
            st.subheader("File preview")
            st.dataframe(df.head(15),use_container_width=True)
            clean,errors=validate_dataframe(df)
            if errors:
                st.error(f"{len(errors)} issue(s) found. Correct the file before importing.")
                st.dataframe(pd.DataFrame(errors),use_container_width=True,hide_index=True)
            else:
                st.success(f"Validation passed: {len(clean)} row(s).")
                if st.button("Import validated data",type="primary"):
                    for _,row in clean.iterrows(): add_academic_record(row)
                    log_event(user["id"],"data_import",f"Imported {len(clean)} records")
                    st.success("Records imported successfully.")
        except Exception as exc: st.error(f"Unable to read file: {exc}")
    st.subheader("Data governance")
    st.caption("Confirm authorization and permitted purpose before processing student data. Restrict raw uploads and avoid logging personal marks or names.")
