
import streamlit as st
import pandas as pd

from app.pages.common import hero

from src.services import (
    get_students,
    get_student_records
)

from src.prediction.service import (
    model_status,
    predict_student,
    validate_student_record
)

from src.training.train_model import (
    train_model_from_database,
    train_demo_model
)

from src.explainability.explainer import (
    explain_prediction
)


# ==========================================
# TRAINING RESULT DISPLAY
# ==========================================

def show_training_result(result, demo=False):

    if result is None:

        st.error(
            "At least 20 valid academic records are required for training."
        )

        return

    label = "Synthetic demo model" if demo else "Database model"

    st.success(
        f"{label} trained successfully!"
    )

    st.write(f"**Selected Algorithm:** {result['model']}")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "MAE",
        f"{result['MAE']:.2f}"
    )

    c2.metric(
        "RMSE",
        f"{result['RMSE']:.2f}"
    )

    c3.metric(
        "R² Score",
        f"{result['R2']:.3f}"
    )

    st.subheader("Algorithm Comparison")

    comparison = pd.DataFrame(
        result["comparison"]
    ).T

    st.dataframe(
        comparison,
        use_container_width=True
    )


# ==========================================
# MAIN PREDICTION PAGE
# ==========================================

def render(user):

    hero(
        "Prediction & what-if studio",
        "Estimate performance, compare scenarios and inspect model drivers."
    )

    # ======================================
    # MODEL STATUS
    # ======================================

    status = model_status()

    st.subheader("Machine Learning Model")

    if status["ready"]:

        st.success("Trained model file detected.")

    else:

        st.warning(
            "No model trained yet. Train using actual academic records "
            "or use clearly labelled synthetic demonstration data."
        )

        a, b = st.columns(2)

        # Database training
        with a:

            if st.button(
                "Train from current database",
                type="primary",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Training model using academic records..."
                    ):

                        result = train_model_from_database()

                    show_training_result(result)

                    if result is not None:
                        st.rerun()

                except Exception as exc:

                    st.error(
                        f"Database training failed: {exc}"
                    )

        # Demo training
        with b:

            if st.button(
                "Train synthetic demo model",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Training synthetic demonstration model..."
                    ):

                        result = train_demo_model()

                    show_training_result(
                        result,
                        demo=True
                    )

                    if result is not None:
                        st.rerun()

                except Exception as exc:

                    st.error(
                        f"Demo training failed: {exc}"
                    )

        st.info(
            "Demo training uses artificially generated data. "
            "Its predictions and evaluation metrics must not be "
            "presented as actual student performance results."
        )

        return

    # ======================================
    # STUDENT SELECTION
    # ======================================

    try:

        students = get_students()

        if students is None or students.empty:

            st.info(
                "No student records are available."
            )

            return

        sid = st.selectbox(
            "Select Student",
            students["student_id"].tolist()
        )

        records = get_student_records(sid)

        if records is None or records.empty:

            st.warning(
                "No academic record found for this student."
            )

            return

        # Latest available academic record
        base = records.iloc[-1].to_dict()

    except Exception as exc:

        st.error(
            f"Unable to retrieve student records: {exc}"
        )

        return

    # ======================================
    # VALIDATE ORIGINAL STUDENT DATA
    # ======================================

    try:

        base = validate_student_record(base)

    except ValueError as exc:

        st.error(
            f"Student academic data is incomplete or invalid: {exc}"
        )

        return

    except Exception as exc:

        st.error(
            f"Student data validation failed: {exc}"
        )

        return

    st.divider()

    # ======================================
    # WHAT-IF ANALYSIS
    # ======================================

    st.subheader("What-if Scenario Analysis")

    st.write(
        "Change the academic inputs below to explore how "
        "different study conditions may affect predicted performance."
    )

    st.caption(
        "These changes are temporary and do not modify the original "
        "student academic records."
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        attendance = st.slider(
            "Attendance (%)",
            min_value=0,
            max_value=100,
            value=int(base["Attendance"]),
            step=1
        )

    with c2:

        study = st.slider(
            "Study Hours / Day",
            min_value=0.0,
            max_value=24.0,
            value=float(base["Study_Hours"]),
            step=0.5
        )

    with c3:

        assignment = st.slider(
            "Assignment Marks",
            min_value=0,
            max_value=100,
            value=int(base["Assignment_Marks"]),
            step=1
        )

    # Create modified scenario
    scenario = {
        **base,
        "Attendance": attendance,
        "Study_Hours": study,
        "Assignment_Marks": assignment
    }

    st.divider()

    # ======================================
    # PERFORMANCE PREDICTION
    # ======================================

    st.subheader("Student Performance Prediction")

    try:

        before = predict_student(base)

        after = predict_student(scenario)

        improvement = after - before

        x, y = st.columns(2)

        with x:

            st.metric(
                "Baseline Estimate",
                f"{before:.2f}/100"
            )

        with y:

            st.metric(
                "Scenario Estimate",
                f"{after:.2f}/100",
                f"{improvement:+.2f}"
            )

        # Prediction comparison
        comparison = pd.DataFrame({

            "Scenario": [
                "Baseline",
                "Modified Scenario"
            ],

            "Predicted Marks": [
                before,
                after
            ]

        })

        st.bar_chart(
            comparison.set_index("Scenario")
        )

        if improvement > 0:

            st.success(
                f"The modified scenario increases the estimated "
                f"marks by {improvement:.2f}."
            )

        elif improvement < 0:

            st.warning(
                f"The modified scenario decreases the estimated "
                f"marks by {abs(improvement):.2f}."
            )

        else:

            st.info(
                "The modified scenario does not change the predicted marks."
            )

        st.caption(
            "Predictions are estimates, not guarantees of actual academic "
            "performance. Results depend on the quality and range of "
            "the training data."
        )

    except Exception as exc:

        st.error(
            f"Prediction error: {exc}"
        )

        return

    st.divider()

    # ======================================
    # SHAP EXPLAINABILITY
    # ======================================

    st.subheader("Prediction Explanation")

    st.write(
        "Understand which academic factors influenced the "
        "predicted student performance."
    )

    try:

        explanation = explain_prediction(scenario)

        if explanation is not None and not explanation.empty:

            st.caption(
                "Positive contributions increase the prediction "
                "relative to the model baseline. Negative contributions "
                "decrease it."
            )

            st.bar_chart(
                explanation.set_index("Feature")["Contribution"]
            )

            st.subheader("Feature Contribution Details")

            display = explanation.copy()

            display["Contribution"] = (
                display["Contribution"].round(3)
            )

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "SHAP explanation is currently unavailable. "
                "Please check the trained model and reference data."
            )

    except Exception as exc:

        st.warning(
            f"Unable to generate prediction explanation: {exc}"
        )

    st.divider()

    # ======================================
    # FINAL INFORMATION
    # ======================================

    st.caption(
        "TREKVERSE | Academic Performance Prediction & "
        "Explainable Machine Learning"
    )
