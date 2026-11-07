# TREKVERSE
## Intelligent Academic Performance Monitoring & Recommendation System

A modular Streamlit application implementing the structure and features in the supplied project proposal.

## Run locally (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/app.py
```

## Demo accounts
- Administrator: `admin` / `Admin@123`
- Faculty: `faculty` / `Faculty@123`
- Student: `student` / `Student@123`

Demo data is synthetic and illustrative. Change demo credentials and use institution-approved data before any real deployment.

## Implemented modules
- Separate Admin, Faculty, Student, Analytics, Prediction and Reports pages
- Role-aware navigation and record access
- Student profile, semester, subject, marks and attendance records
- Student directory, trends, subject comparisons and risk distribution
- ML training and evaluation (Linear Regression and Random Forest, holdout MAE/RMSE/R²)
- Model-backed what-if simulator that does not overwrite original records
- Explainability module with optional SHAP feature attributions and safe fallback
- Configurable transparent Low / Moderate / High risk rules
- CSV/XLSX import, validation, preview and actionable row errors
- K-Means engagement segmentation (only when enough records exist)
- Personalized weekly study planner with editable task completion in the UI
- Faculty intervention tracking
- PDF academic report generation
- SQLite schema and persistence, audit log

## Data import format
Required columns:
`Student_ID, Attendance, Internal_Marks, Assignment_Marks, Quiz_Marks, Study_Hours, Previous_CGPA, Backlogs, Final_Marks`

Optional:
`Name, Department, Semester, Subject`

Ranges: attendance and marks 0–100; CGPA 0–10; study hours non-negative; backlogs non-negative integer. `Final_Marks` is the target and is never used as an input feature.

## Project notes
- Local SQLite is used for a reproducible demonstration. A production college deployment should use PostgreSQL/MySQL, HTTPS, secure secrets, backups, institutional identity management and security review.
- Demo records and the generated demo training dataset are synthetic, not real institutional evidence.
- Risk thresholds are configurable in `src/recommendations/risk.py`; institutions must review thresholds, false alarms and missed cases.
- Predictions and SHAP values are estimates/associations, not causal explanations or guarantees. Faculty must review risk flags.
- Student accounts are limited to their linked student record. Faculty demo view is provided for demonstration; map faculty to assigned classes before deployment.
- Do not commit real student data, database files, passwords, or model artifacts.
