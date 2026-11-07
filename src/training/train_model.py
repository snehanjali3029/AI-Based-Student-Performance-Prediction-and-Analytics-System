
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from src.feature_engineering.features import FEATURE_COLUMNS
from database.database import get_connection


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "model_registry"
    / "performance_model.joblib"
)


def _fit(X, y):

    Xtr, Xte, ytr, yte = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    candidates = {
        "Linear Regression": LinearRegression(),

        "Random Forest": RandomForestRegressor(
            n_estimators=180,
            min_samples_leaf=2,
            random_state=42
        )
    }

    results = {}
    best = None
    best_mae = float("inf")
    best_name = ""

    for name, model in candidates.items():

        model.fit(Xtr, ytr)

        pred = model.predict(Xte)

        mae = mean_absolute_error(yte, pred)

        cv = -cross_val_score(
            model,
            X,
            y,
            cv=5,
            scoring="neg_mean_absolute_error"
        ).mean()

        results[name] = {
            "MAE": mae,
            "RMSE": mean_squared_error(yte, pred) ** 0.5,
            "R2": r2_score(yte, pred),
            "CV_MAE": cv
        }

        if mae < best_mae:
            best = model
            best_mae = mae
            best_name = name

    # Prepare background data for SHAP
    background = X.sample(
        n=min(100, len(X)),
        random_state=42
    ).copy()

    # Save trained model and SHAP background data
    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": best,
            "features": FEATURE_COLUMNS,
            "name": best_name,
            "background": background
        },
        MODEL_PATH
    )

    return {
        "MAE": results[best_name]["MAE"],
        "RMSE": results[best_name]["RMSE"],
        "R2": results[best_name]["R2"],
        "CV_MAE": results[best_name]["CV_MAE"],
        "model": best_name,
        "comparison": results
    }


def train_model_from_database():

    connection = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            attendance AS Attendance,
            internal_marks AS Internal_Marks,
            assignment_marks AS Assignment_Marks,
            quiz_marks AS Quiz_Marks,
            study_hours AS Study_Hours,
            previous_cgpa AS Previous_CGPA,
            backlogs AS Backlogs,
            final_marks AS Final_Marks
        FROM academic_records
        """,
        connection
    )

    connection.close()

    df = df.dropna()

    if len(df) < 8:
        return None

    return _fit(
        df[FEATURE_COLUMNS],
        df["Final_Marks"]
    )


def train_demo_model():

    rng = np.random.default_rng(42)

    n = 700

    X = pd.DataFrame({
        "Attendance": rng.uniform(40, 100, n),
        "Internal_Marks": rng.uniform(20, 100, n),
        "Assignment_Marks": rng.uniform(20, 100, n),
        "Quiz_Marks": rng.uniform(20, 100, n),
        "Study_Hours": rng.uniform(0, 7, n),
        "Previous_CGPA": rng.uniform(4, 10, n),
        "Backlogs": rng.integers(0, 4, n)
    })

    y = (
        0.20 * X.Attendance
        + 0.22 * X.Internal_Marks
        + 0.15 * X.Assignment_Marks
        + 0.13 * X.Quiz_Marks
        + 1.5 * X.Study_Hours
        + 2 * X.Previous_CGPA
        - 2 * X.Backlogs
        + rng.normal(0, 6, n)
    ).clip(0, 100)

    return _fit(X, y)
