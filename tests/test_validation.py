import pandas as pd
from src.preprocessing.validation import validate_dataframe
def test_valid_row():
    df=pd.DataFrame([{"Student_ID":"S1","Attendance":80,"Internal_Marks":70,"Assignment_Marks":75,"Quiz_Marks":72,"Study_Hours":2,"Previous_CGPA":7.5,"Backlogs":0,"Final_Marks":78}])
    clean,errors=validate_dataframe(df);assert len(clean)==1 and not errors
def test_invalid_attendance():
    df=pd.DataFrame([{"Student_ID":"S1","Attendance":120,"Internal_Marks":70,"Assignment_Marks":75,"Quiz_Marks":72,"Study_Hours":2,"Previous_CGPA":7.5,"Backlogs":0,"Final_Marks":78}])
    _,errors=validate_dataframe(df);assert any(x["Column"]=="Attendance" for x in errors)
