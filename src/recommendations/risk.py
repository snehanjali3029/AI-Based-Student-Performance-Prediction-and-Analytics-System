
import math


# --------------------------------------------------
# 1. FIELD ALIASES
# --------------------------------------------------

ALIASES = {
    "Attendance": [
        "Attendance",
        "attendance",
        "Attendance_Percentage"
    ],
    "Previous_CGPA": [
        "Previous_CGPA",
        "previous_cgpa",
        "CGPA",
        "cgpa"
    ],
    "Backlogs": [
        "Backlogs",
        "backlogs",
        "No_of_Backlogs"
    ],
    "Internal_Marks": [
        "Internal_Marks",
        "internal_marks",
        "Internal",
        "internal"
    ],
    "Assignment_Marks": [
        "Assignment_Marks",
        "assignment_marks",
        "Assignment"
    ],
    "Quiz_Marks": [
        "Quiz_Marks",
        "quiz_marks",
        "Quiz"
    ],
    "Final_Marks": [
        "Final_Marks",
        "final_marks",
        "Final"
    ]
}


# --------------------------------------------------
# 2. SAFE VALUE RETRIEVAL
# --------------------------------------------------

def get_value(record, key, default=None):
    """
    Retrieve numeric values safely.
    Supports aliases, missing values and NaN.
    """

    if record is None:
        return default

    possible_keys = ALIASES.get(key, [key])

    for field in possible_keys:

        value = record.get(field)

        if value is None or value == "":
            continue

        try:
            number = float(value)

            if math.isnan(number) or math.isinf(number):
                continue

            return number

        except (TypeError, ValueError):
            continue

    return default


# --------------------------------------------------
# 3. ASSESS STUDENT RISK
# --------------------------------------------------

def assess_risk(record):
    """
    Assess academic performance using configured thresholds.

    Returns:
        risk level
        list of review reasons
    """

    if record is None or len(record) == 0:
        return "Insufficient Data", [
            "No academic record available"
        ]

    attendance = get_value(record, "Attendance")
    cgpa = get_value(record, "Previous_CGPA")
    backlogs = get_value(record, "Backlogs")
    internal_marks = get_value(record, "Internal_Marks")

    reasons = []
    missing = []

    # Required academic information
    if attendance is None:
        missing.append("Attendance")

    if internal_marks is None:
        missing.append("Internal assessment marks")

    # Insufficient data should not be classified
    # as actual academic risk.
    if missing:

        reasons.append(
            "Missing academic information: "
            + ", ".join(missing)
        )

        return "Insufficient Data", reasons

    # --------------------------------------------------
    # 4. ATTENDANCE REVIEW
    # --------------------------------------------------

    if attendance < 65:

        reasons.append(
            "Attendance is below the configured "
            "65% review threshold"
        )

    # --------------------------------------------------
    # 5. CGPA REVIEW
    # --------------------------------------------------

    if cgpa is not None and cgpa < 6.0:

        reasons.append(
            "Previous CGPA is below the configured "
            "6.0 review threshold"
        )

    # --------------------------------------------------
    # 6. BACKLOG REVIEW
    # --------------------------------------------------

    if backlogs is not None and backlogs >= 2:

        reasons.append(
            "Two or more previous backlogs are recorded"
        )

    # --------------------------------------------------
    # 7. INTERNAL MARKS REVIEW
    # --------------------------------------------------

    if internal_marks < 40:

        reasons.append(
            "Internal assessment marks need review"
        )

    # --------------------------------------------------
    # 8. RISK CLASSIFICATION
    # --------------------------------------------------

    if len(reasons) >= 2:
        return "High", reasons

    if len(reasons) == 1:
        return "Moderate", reasons

    return "Low", [
        "Current indicators do not cross configured "
        "review thresholds"
    ]


# --------------------------------------------------
# 9. PERSONALIZED RECOMMENDATIONS
# --------------------------------------------------

def recommendations_for(record):
    """
    Generate personalized academic recommendations.
    Missing values are not treated as poor performance.
    """

    if record is None or len(record) == 0:

        return [
            "Add academic records to generate relevant guidance."
        ]

    tips = []

    attendance = get_value(record, "Attendance")
    internal_marks = get_value(record, "Internal_Marks")
    assignment_marks = get_value(record, "Assignment_Marks")
    cgpa = get_value(record, "Previous_CGPA")
    backlogs = get_value(record, "Backlogs")

    # --------------------------------------------------
    # ATTENDANCE RECOMMENDATION
    # --------------------------------------------------

    if attendance is not None and attendance < 75:

        tips.append(
            "Agree an attendance improvement plan and "
            "review barriers with faculty."
        )

    # --------------------------------------------------
    # INTERNAL MARKS RECOMMENDATION
    # --------------------------------------------------

    if internal_marks is not None and internal_marks < 60:

        tips.append(
            "Schedule short, regular practice sessions "
            "for topics covered in internal assessments."
        )

    # --------------------------------------------------
    # ASSIGNMENT RECOMMENDATION
    # --------------------------------------------------

    if assignment_marks is not None and assignment_marks < 60:

        tips.append(
            "Break assignments into smaller milestones "
            "and track submission progress."
        )

    # --------------------------------------------------
    # CGPA RECOMMENDATION
    # --------------------------------------------------

    if cgpa is not None and cgpa < 7:

        tips.append(
            "Meet the faculty mentor to identify two "
            "priority subjects for targeted support."
        )

    # --------------------------------------------------
    # BACKLOG RECOMMENDATION
    # --------------------------------------------------

    if backlogs is not None and backlogs > 0:

        tips.append(
            "Create a backlog revision plan using "
            "previous question papers and weekly mock tests."
        )

    # --------------------------------------------------
    # MISSING DATA GUIDANCE
    # --------------------------------------------------

    missing = []

    if attendance is None:
        missing.append("attendance")

    if internal_marks is None:
        missing.append("internal marks")

    if missing:

        tips.append(
            "Update missing academic information: "
            + ", ".join(missing)
            + "."
        )

    # --------------------------------------------------
    # GENERAL RECOMMENDATION
    # --------------------------------------------------

    if not tips:

        tips.append(
            "Maintain the current study routine and "
            "review progress after the next assessment."
        )

    return tips
