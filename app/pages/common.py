
import streamlit as st
import pandas as pd

from src.services import (
    get_students,
    get_student,
    get_student_records,
    get_dashboard_stats,
    get_interventions,
    save_intervention
)

from src.recommendations.risk import (
    assess_risk,
    recommendations_for
)


def hero(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True
    )


def metric_row(stats):
    a, b, c, d = st.columns(4)

    a.metric("Total students", stats["total"])
    b.metric("Average CGPA", f'{stats["cgpa"]:.2f}')
    c.metric("Average attendance", f'{stats["attendance"]:.1f}%')
    d.metric("Students requiring support", stats["support"])


def display_value(value, suffix="", decimals=1):
    if value is None or pd.isna(value):
        return "Not available"

    return f"{float(value):.{decimals}f}{suffix}"


def student_table():

    df = get_students()
    rows = []

    for _, s in df.iterrows():

        rec = get_student_records(s.student_id)

        latest = rec.iloc[-1].to_dict() if not rec.empty else {}

        risk, _ = assess_risk(latest)

        rows.append({
            "Student ID": s.student_id,
            "Name": s.name,
            "Department": s.department,
            "Semester": s.semester,
            "CGPA": s.previous_cgpa,
            "Attendance": display_value(
                latest.get("Attendance"),
                "%"
            ),
            "Risk": risk
        })

    return pd.DataFrame(rows)


def student_detail(sid, user, allow_intervention=False):

    s = get_student(sid)

    if not s:
        st.warning("Student profile not found.")
        return

    records = get_student_records(sid)

    st.subheader(f"{s['name']} · {sid}")

    st.caption(
        f"{s['department']} · Semester {s['semester']}"
    )

    if records.empty:
        st.info("No academic records available.")
        return

    latest = records.iloc[-1].to_dict()

    risk, reasons = assess_risk(latest)

    a, b, c = st.columns(3)

    attendance = latest.get("Attendance")
    final_marks = latest.get("Final_Marks")

    a.metric(
        "Attendance",
        display_value(attendance, "%")
    )

    b.metric(
        "Latest marks",
        display_value(final_marks, "/100")
    )

    c.metric(
        "Support indicator",
        risk
    )

    st.write("**Factors for review**")

    for reason in reasons:
        st.write("•", reason)

    st.write("**Recommended support**")

    for tip in recommendations_for(latest):
        st.write("•", tip)

    if allow_intervention:

        with st.expander("Record faculty intervention"):

            with st.form(f"intervention_{sid}"):

                action = st.text_area(
                    "Intervention / follow-up plan"
                )

                status = st.selectbox(
                    "Status",
                    ["Open", "In progress", "Completed"]
                )

                if st.form_submit_button("Save intervention"):

                    if action.strip():

                        save_intervention(
                            sid,
                            user["id"],
                            action.strip(),
                            status
                        )

                        st.success("Follow-up saved.")

                    else:
                        st.warning("Please enter an intervention plan.")

        history = get_interventions(sid)

        if history:

            st.write("**Intervention history**")

            st.dataframe(
                pd.DataFrame(history),
                use_container_width=True,
                hide_index=True
            )
