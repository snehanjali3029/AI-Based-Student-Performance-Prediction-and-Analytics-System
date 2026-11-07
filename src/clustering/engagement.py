
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def segment_engagement(frame):
    """
    Exploratory student engagement grouping.

    Uses attendance, study hours and assignment marks.
    Segment labels are exploratory only and are not
    student ability or academic risk judgments.
    """

    cols = ["Attendance", "Study_Hours", "Assignment_Marks"]

    # Check whether required columns exist
    if frame is None or not all(col in frame.columns for col in cols):
        return None

    # Select required columns and convert to numeric
    data = frame[cols].copy()

    for col in cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # Remove missing and infinite values
    data = data.replace([float("inf"), float("-inf")], float("nan"))
    data = data.dropna()

    # Require at least six complete records
    if len(data) < 6:
        return None

    # Avoid clustering when all records are identical
    if data.drop_duplicates().shape[0] < 2:
        return None

    # Standardize features
    scaler = StandardScaler()
    scaled = scaler.fit_transform(data)

    # Create engagement clusters
    k = min(3, len(data) // 2)

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    data["Segment"] = model.fit_predict(scaled)

    return data
