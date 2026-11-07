# Project structure (matches proposal page 10)

```text
TREKVERSE/
├── app/
│   ├── app.py
│   └── pages/
│       ├── admin.py
│       ├── faculty.py
│       ├── student.py
│       ├── analytics.py
│       ├── prediction.py
│       └── reports.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── uploads/
├── models/
│   ├── model_registry/
│   └── preprocessor/
├── src/
│   ├── preprocessing/
│   ├── feature_engineering/
│   ├── training/
│   ├── prediction/
│   ├── explainability/
│   ├── recommendations/
│   └── clustering/
├── database/
│   ├── schema.sql
│   └── database.py
├── reports/
│   └── report_generator.py
├── tests/
├── requirements.txt
└── README.md
```

Implementation files are placed inside each named module. The UI is routed through the six dedicated page modules instead of putting all functionality into `app.py`.
