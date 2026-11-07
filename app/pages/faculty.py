import streamlit as st
from app.pages.common import hero,metric_row,student_table,student_detail
from src.services import get_dashboard_stats

def render_overview(user):
    hero("Faculty workspace","Identify learning needs, review student context and coordinate support.")
    metric_row(get_dashboard_stats())
    df=student_table()
    st.subheader("Academic support queue")
    if not df.empty:
        st.dataframe(df[df["Risk"]!="Low"].sort_values(["Risk","Attendance"]),use_container_width=True,hide_index=True)
        sid=st.selectbox("Review a student",df["Student ID"].tolist())
        student_detail(sid,user,allow_intervention=True)


def render_directory(user):
    hero(
        "Student directory",
        "Review profiles, academic history and follow-up actions."
    )

    df = student_table()

    if df.empty:
        st.info("No student records available.")
        return

    q = st.text_input(
        "Search student",
        placeholder="Enter Student ID, name, department or risk level...",
        key="faculty_student_search"
    ).strip()

    if q:
        searchable_columns = [
            col for col in [
                "Student ID",
                "Name",
                "Department",
                "Semester",
                "CGPA",
                "Attendance",
                "Risk"
            ]
            if col in df.columns
        ]

        mask = df[searchable_columns].apply(
            lambda column: column.astype(str).str.contains(
                q,
                case=False,
                na=False,
                regex=False
            )
        ).any(axis=1)

        filtered_df = df.loc[mask].copy()

        st.caption(
            f"Found {len(filtered_df)} student(s)."
        )
    else:
        filtered_df = df.copy()

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    if not filtered_df.empty:
        sid = st.selectbox(
            "Open student profile",
            filtered_df["Student ID"].tolist(),
            key="faculty_open_student"
        )

        student_detail(
            sid,
            user,
            allow_intervention=True
        )
    elif q:
        st.warning("No matching student found. Try another search.")

