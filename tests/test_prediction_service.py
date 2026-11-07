
import pytest

from src.prediction.service import validate_student_record


# --------------------------------------------------
# TEST DATA
# --------------------------------------------------

@pytest.fixture
def valid_record():

    return {
        "Attendance": 85,
        "Internal_Marks": 80,
        "Assignment_Marks": 90,
        "Quiz_Marks": 75,
        "Study_Hours": 6,
        "Previous_CGPA": 8.5,
        "Backlogs": 0
    }


# --------------------------------------------------
# VALID INPUT TESTS
# --------------------------------------------------

def test_valid_student_record(valid_record):

    result = validate_student_record(valid_record)

    assert result["Attendance"] == 85
    assert result["Previous_CGPA"] == 8.5
    assert result["Backlogs"] == 0


# --------------------------------------------------
# MISSING INPUT TEST
# --------------------------------------------------

def test_missing_feature(valid_record):

    del valid_record["Internal_Marks"]

    with pytest.raises(ValueError):
        validate_student_record(valid_record)


# --------------------------------------------------
# INVALID INPUT TYPE TEST
# --------------------------------------------------

def test_invalid_input_type():

    with pytest.raises(ValueError):
        validate_student_record("invalid")


# --------------------------------------------------
# NAN VALUE TEST
# --------------------------------------------------

def test_nan_value(valid_record):

    valid_record["Attendance"] = float("nan")

    with pytest.raises(ValueError):
        validate_student_record(valid_record)


# --------------------------------------------------
# ATTENDANCE VALIDATION TEST
# --------------------------------------------------

def test_attendance_out_of_range(valid_record):

    valid_record["Attendance"] = 120

    with pytest.raises(ValueError):
        validate_student_record(valid_record)


# --------------------------------------------------
# MARKS VALIDATION TEST
# --------------------------------------------------

def test_negative_marks(valid_record):

    valid_record["Internal_Marks"] = -5

    with pytest.raises(ValueError):
        validate_student_record(valid_record)


# --------------------------------------------------
# STUDY HOURS VALIDATION TEST
# --------------------------------------------------

def test_study_hours_exceed_limit(valid_record):

    valid_record["Study_Hours"] = 25

    with pytest.raises(ValueError):
        validate_student_record(valid_record)


# --------------------------------------------------
# CGPA VALIDATION TESTS
# --------------------------------------------------

def test_negative_cgpa(valid_record):

    valid_record["Previous_CGPA"] = -1

    with pytest.raises(ValueError):
        validate_student_record(valid_record)


def test_cgpa_above_10(valid_record):

    valid_record["Previous_CGPA"] = 11

    with pytest.raises(ValueError):
        validate_student_record(valid_record)


# --------------------------------------------------
# BACKLOG VALIDATION TEST
# --------------------------------------------------

def test_fractional_backlogs(valid_record):

    valid_record["Backlogs"] = 1.5

    with pytest.raises(ValueError):
        validate_student_record(valid_record)
