
import pandas as pd

from src.services import get_students, get_student_records
from src.recommendations.risk import assess_risk


def cohort_dataframe():

    # Fetch all students
    students = get_students()

    rows = []

    # Check whether student data exists
    if students is None or students.empty:
        return pd.DataFrame()

    for _, student in students.iterrows():

        # Fetch academic records for the current student
        records = get_student_records(student.student_id)

        if records is None or records.empty:
            continue

        # Get the latest available academic record
        record = records.iloc[-1].to_dict()

        # Include previous CGPA from student profile
        record["Previous_CGPA"] = student.previous_cgpa

        # Calculate academic risk
        risk, reasons = assess_risk(record)

        # Prepare student analytics data
        rows.append({
            "Student ID": student.student_id,
            "Department": student.department,
            "CGPA": student.previous_cgpa,
            "Attendance": record.get("Attendance"),
            "Internal_Marks": record.get("Internal_Marks"),
            "Assignment_Marks": record.get("Assignment_Marks"),
            "Quiz_Marks": record.get("Quiz_Marks"),
            "Study_Hours": record.get("Study_Hours"),
            "Final_Marks": record.get("Final_Marks"),
            "Risk": risk
        })

    # Convert collected records into DataFrame
    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Convert analytical columns into numeric values
    numeric_columns = [
        "CGPA",
        "Attendance",
        "Internal_Marks",
        "Assignment_Marks",
        "Quiz_Marks",
        "Study_Hours",
        "Final_Marks"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df
