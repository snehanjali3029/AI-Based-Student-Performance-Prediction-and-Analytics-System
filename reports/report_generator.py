
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape
import re

import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm

from src.recommendations.risk import (
    assess_risk,
    recommendations_for
)


# --------------------------------------------------
# 1. SAFE VALUE FUNCTIONS
# --------------------------------------------------

def safe_float(value, default=0.0):
    try:
        if pd.isna(value) or value == "":
            return default

        return float(value)

    except (ValueError, TypeError):
        return default


def display_value(value, suffix=""):

    if value is None or pd.isna(value) or value == "":
        return "N/A"

    number = safe_float(value, None)

    if number is not None:
        return f"{number:.1f}{suffix}"

    return f"{escape(str(value))}{suffix}"


def get_student_cgpa(student):

    if not student:
        return None

    possible_keys = [
        "previous_cgpa",
        "Previous_CGPA",
        "CGPA",
        "cgpa"
    ]

    for key in possible_keys:

        value = student.get(key)

        if value is not None and not pd.isna(value) and value != "":
            return safe_float(value, None)

    return None


def make_paragraph(value, style):

    return Paragraph(
        escape(str(value)),
        style
    )


# --------------------------------------------------
# 2. FIND THE LATEST ACADEMIC RECORD
# --------------------------------------------------

def get_latest_record(records):

    if records is None or records.empty:
        return None

    # Common date column names
    date_columns = [
        "date",
        "timestamp",
        "created_at",
        "updated_at",
        "record_date",
        "assessment_date",
        "exam_date"
    ]

    # Normalize column names
    column_map = {
        re.sub(r"[^a-z0-9]", "", str(col).lower()): col
        for col in records.columns
    }

    selected_column = None

    for name in date_columns:

        normalized = re.sub(r"[^a-z0-9]", "", name)

        if normalized in column_map:
            selected_column = column_map[normalized]
            break

    # Also check other columns containing date/time
    if selected_column is None:

        for col in records.columns:

            normalized = re.sub(
                r"[^a-z0-9]",
                "",
                str(col).lower()
            )

            if "date" in normalized or "timestamp" in normalized:
                selected_column = col
                break

    # Use date column if available
    if selected_column is not None:

        parsed_dates = pd.to_datetime(
            records[selected_column],
            errors="coerce"
        )

        if parsed_dates.notna().any():

            latest_position = parsed_dates.argmax()

            return records.iloc[latest_position].to_dict()

    # Fallback:
    # If there is no usable date column, use the last CSV row.
    # CSV should be arranged oldest to newest.

    return records.iloc[-1].to_dict()


# --------------------------------------------------
# 3. CREATE STUDENT PDF
# --------------------------------------------------

def create_student_pdf(student, records):

    buf = BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="Brand",
            parent=styles["Title"],
            textColor=colors.HexColor("#18385d"),
            fontSize=22,
            spaceAfter=5
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["Normal"],
            fontSize=9,
            leading=13
        )
    )

    story = [

        Paragraph("TREKVERSE", styles["Brand"]),

        Paragraph(
            "Academic Performance Monitoring Report",
            styles["Heading2"]
        ),

        Paragraph(
            f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
            styles["Normal"]
        ),

        Spacer(1, 12)
    ]

    # --------------------------------------------------
    # 4. STUDENT INFORMATION
    # --------------------------------------------------

    if student:

        cgpa = get_student_cgpa(student)

        student_data = [

            [
                "Student ID",
                escape(str(student.get("student_id", "N/A")))
            ],

            [
                "Name",
                escape(str(student.get("name", "N/A")))
            ],

            [
                "Department",
                escape(str(student.get("department", "N/A")))
            ],

            [
                "Semester",
                escape(str(student.get("semester", "N/A")))
            ],

            [
                "Previous CGPA",
                display_value(cgpa)
                if cgpa is not None
                else "N/A"
            ]
        ]

        table = Table(
            student_data,
            colWidths=[45 * mm, 110 * mm]
        )

        table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#edf3f8")
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#d5dfeb")
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story += [
            table,
            Spacer(1, 14)
        ]

    # --------------------------------------------------
    # 5. ACADEMIC PERFORMANCE
    # --------------------------------------------------

    latest_record = get_latest_record(records)

    if latest_record is not None:

        r = latest_record.copy()

        # Synchronize CGPA from student profile
        student_cgpa = get_student_cgpa(student)

        if student_cgpa is not None:

            # Student profile is authoritative
            r["Previous_CGPA"] = student_cgpa

        # Existing risk assessment logic
        risk, reasons = assess_risk(r)

        # Academic values
        attendance = r.get("Attendance")
        internal = r.get("Internal_Marks")
        assignment = r.get("Assignment_Marks")
        quiz = r.get("Quiz_Marks")
        final_marks = r.get("Final_Marks")

        performance_data = [

            ["Measure", "Latest recorded value"],

            [
                "Attendance",
                display_value(attendance, "%")
            ],

            [
                "Internal marks",
                display_value(internal)
            ],

            [
                "Assignment marks",
                display_value(assignment)
            ],

            [
                "Quiz marks",
                display_value(quiz)
            ],

            [
                "Final marks",
                display_value(final_marks) + "/100"
                if final_marks is not None
                and not pd.isna(final_marks)
                and final_marks != ""
                else "N/A"
            ],

            [
                "Support indicator",
                escape(str(risk))
            ]
        ]

        # Convert cells to Paragraphs for proper wrapping
        performance_data = [
            [
                make_paragraph(cell, styles["Normal"])
                for cell in row
            ]
            for row in performance_data
        ]

        table = Table(
            performance_data,
            colWidths=[65 * mm, 90 * mm],
            repeatRows=1
        )

        table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#18385d")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#d5dfeb")
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ])
        )

        story += [

            Paragraph(
                "Academic performance",
                styles["Heading2"]
            ),

            table,

            Spacer(1, 12),

            Paragraph(
                "Factors for review",
                styles["Heading2"]
            )
        ]

        # --------------------------------------------------
        # 6. RISK FACTORS
        # --------------------------------------------------

        if reasons:

            for reason in reasons:

                story.append(
                    Paragraph(
                        "• " + escape(str(reason)),
                        styles["Normal"]
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No specific risk factors identified.",
                    styles["Normal"]
                )
            )

        # --------------------------------------------------
        # 7. STUDY RECOMMENDATIONS
        # --------------------------------------------------

        story += [

            Spacer(1, 8),

            Paragraph(
                "Study support recommendations",
                styles["Heading2"]
            )
        ]

        recommendations = recommendations_for(r)

        if recommendations:

            for item in recommendations:

                story.append(
                    Paragraph(
                        "• " + escape(str(item)),
                        styles["Normal"]
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No additional recommendations available.",
                    styles["Normal"]
                )
            )

    else:

        story.append(
            Paragraph(
                "No academic records available for this student.",
                styles["Normal"]
            )
        )

    # --------------------------------------------------
    # 8. DISCLAIMER
    # --------------------------------------------------

    story += [

        Spacer(1, 16),

        Paragraph(
            "Disclaimer: Model outputs are estimates and may be "
            "inaccurate or incomplete. They should be reviewed with "
            "actual academic context by authorized faculty and must "
            "not be the sole basis for consequential decisions.",

            styles["Italic"]
        )
    ]

    # --------------------------------------------------
    # 9. GENERATE PDF
    # --------------------------------------------------

    doc.build(story)

    return buf.getvalue()
