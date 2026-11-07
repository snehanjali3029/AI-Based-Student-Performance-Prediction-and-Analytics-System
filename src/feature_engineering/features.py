FEATURE_COLUMNS=["Attendance","Internal_Marks","Assignment_Marks","Quiz_Marks","Study_Hours","Previous_CGPA","Backlogs"]
def build_features(frame):
    """Select consistent prediction-time inputs; target Final_Marks is deliberately excluded."""
    return frame[FEATURE_COLUMNS].copy()
