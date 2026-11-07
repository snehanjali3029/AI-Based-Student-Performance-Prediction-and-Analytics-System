import pandas as pd
REQUIRED_COLUMNS=["Student_ID","Attendance","Internal_Marks","Assignment_Marks","Quiz_Marks","Study_Hours","Previous_CGPA","Backlogs","Final_Marks"]
NUMERIC=["Attendance","Internal_Marks","Assignment_Marks","Quiz_Marks","Study_Hours","Previous_CGPA","Backlogs","Final_Marks"]
def validate_dataframe(df):
    df=df.copy(); errors=[]
    missing=[x for x in REQUIRED_COLUMNS if x not in df.columns]
    if missing: return pd.DataFrame(),[{"Row":"File","Column":x,"Issue":"Required column missing"} for x in missing]
    df["Student_ID"]=df["Student_ID"].astype(str).str.strip()
    for col in NUMERIC:
        df[col]=pd.to_numeric(df[col],errors="coerce")
        for i in df.index[df[col].isna()]: errors.append({"Row":int(i)+2,"Column":col,"Issue":"Must be numeric"})
    for col in ["Attendance","Internal_Marks","Assignment_Marks","Quiz_Marks","Final_Marks"]:
        for i in df.index[df[col].notna() & ~df[col].between(0,100)]:
            errors.append({"Row":int(i)+2,"Column":col,"Issue":"Must be between 0 and 100"})
    for i in df.index[df["Previous_CGPA"].notna() & ~df["Previous_CGPA"].between(0,10)]:
        errors.append({"Row":int(i)+2,"Column":"Previous_CGPA","Issue":"Must be between 0 and 10"})
    for i in df.index[df["Study_Hours"].notna() & (df["Study_Hours"]<0)]:
        errors.append({"Row":int(i)+2,"Column":"Study_Hours","Issue":"Must be non-negative"})
    for i in df.index[df["Backlogs"].notna() & ((df["Backlogs"]<0)|(df["Backlogs"]%1!=0))]:
        errors.append({"Row":int(i)+2,"Column":"Backlogs","Issue":"Must be a non-negative integer"})
    for i in df.index[df["Student_ID"].duplicated(keep=False)]:
        errors.append({"Row":int(i)+2,"Column":"Student_ID","Issue":"Duplicate ID in upload"})
    return df,errors
