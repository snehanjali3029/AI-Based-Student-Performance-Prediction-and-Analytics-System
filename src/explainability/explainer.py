
import numpy as np
import pandas as pd
import shap

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

from src.prediction.service import load_model
from src.feature_engineering.features import FEATURE_COLUMNS


def explain_prediction(record):

    try:

        # Validate input
        if not isinstance(record, dict):
            raise ValueError(
                "Student record must be a dictionary."
            )

        # Load trained model
        bundle = load_model()

        model = bundle["model"]

        background = bundle.get("background")

        # Check reference data
        if background is None:
            raise ValueError(
                "SHAP reference data missing. Please retrain the model."
            )

        # Check feature compatibility
        if list(bundle.get("features", [])) != FEATURE_COLUMNS:
            raise ValueError(
                "Model features do not match current feature columns."
            )

        # Validate student input
        values = {}

        for feature in FEATURE_COLUMNS:

            if feature not in record or record[feature] is None:
                raise ValueError(
                    f"Missing student information: {feature}"
                )

            try:
                value = float(record[feature])
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid value for {feature}."
                )

            if not np.isfinite(value):
                raise ValueError(
                    f"{feature} must be a finite number."
                )

            values[feature] = value

        # Prepare student input
        x = pd.DataFrame(
            [values],
            columns=FEATURE_COLUMNS
        )

        # Validate background dataset
        if not isinstance(background, pd.DataFrame):
            raise ValueError(
                "Invalid SHAP background dataset."
            )

        if not all(
            feature in background.columns
            for feature in FEATURE_COLUMNS
        ):
            raise ValueError(
                "SHAP background features are incomplete."
            )

        background = background[FEATURE_COLUMNS].copy()

        if background.empty or background.isnull().any().any():
            raise ValueError(
                "SHAP background dataset is empty or contains missing values."
            )

        # Select SHAP explainer
        if isinstance(model, LinearRegression):

            explainer = shap.LinearExplainer(
                model,
                background
            )

        elif isinstance(model, RandomForestRegressor):

            explainer = shap.TreeExplainer(model)

        else:
            raise ValueError(
                f"Unsupported model: {type(model).__name__}"
            )

        # Calculate SHAP values
        shap_values = explainer.shap_values(x)

        # Handle SHAP output
        shap_values = np.asarray(shap_values)

        if shap_values.ndim == 2:
            contributions = shap_values[0]

        elif shap_values.ndim == 1:
            contributions = shap_values

        else:
            raise ValueError(
                "Unexpected SHAP output dimensions."
            )

        if len(contributions) != len(FEATURE_COLUMNS):
            raise ValueError(
                "SHAP feature contribution count mismatch."
            )

        # Prepare explanation results
        result = pd.DataFrame({

            "Feature": FEATURE_COLUMNS,

            "Contribution": [
                float(value)
                for value in contributions
            ]

        })

        # Sort by contribution importance
        result = result.sort_values(
            by="Contribution",
            key=abs,
            ascending=False
        ).reset_index(drop=True)

        return result

    except Exception as error:

        print(
            f"SHAP explanation error: {error}"
        )

        return None
