
import pandas as pd

from database.database import get_connection
from src.recommendations.risk import assess_risk


# --------------------------------------------------
# 1. GET ALL STUDENTS
# --------------------------------------------------

def get_students():
    c = get_connection()

    try:
        df = pd.read_sql_query(
            "SELECT * FROM students ORDER BY student_id",
            c
        )
        return df
    finally:
        c.close()


# --------------------------------------------------
# 2. GET SINGLE STUDENT
# --------------------------------------------------

def get_student(sid):
    c = get_connection()

    try:
        row = c.execute(
            "SELECT * FROM students WHERE student_id=?",
            (sid,)
        ).fetchone()

        return dict(row) if row else None
    finally:
        c.close()


# --------------------------------------------------
# 3. GET STUDENT ACADEMIC RECORDS
# --------------------------------------------------

def get_student_records(sid):
    c = get_connection()

    try:
        df = pd.read_sql_query(
            """
            SELECT
                a.attendance AS Attendance,
                a.internal_marks AS Internal_Marks,
                a.assignment_marks AS Assignment_Marks,
                a.quiz_marks AS Quiz_Marks,
                a.study_hours AS Study_Hours,
                a.previous_cgpa AS Previous_CGPA,
                a.backlogs AS Backlogs,
                a.final_marks AS Final_Marks,
                a.recorded_at,
                s.subject_name AS Subject

            FROM academic_records a

            LEFT JOIN subjects s
                ON a.subject_id = s.id

            WHERE a.student_id=?

            ORDER BY a.id DESC
            """,
            c,
            params=(sid,)
        )

        return df
    finally:
        c.close()


# --------------------------------------------------
# 4. GET DASHBOARD STATISTICS
# --------------------------------------------------

def get_dashboard_stats():

    c = get_connection()

    try:
        total = c.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        cgpa = c.execute(
            "SELECT AVG(previous_cgpa) FROM students"
        ).fetchone()[0] or 0

        rows = c.execute(
            """
            SELECT
                a.student_id,
                a.attendance,
                a.internal_marks,
                a.assignment_marks,
                a.quiz_marks,
                a.study_hours,
                a.previous_cgpa,
                a.backlogs,
                a.final_marks,
                s.previous_cgpa AS profile_cgpa

            FROM academic_records a

            INNER JOIN (
                SELECT student_id, MAX(id) AS latest_id
                FROM academic_records
                GROUP BY student_id
            ) latest
                ON a.id = latest.latest_id

            INNER JOIN students s
                ON a.student_id = s.student_id
            """
        ).fetchall()

        risks = []

        attendances = []

        for row in rows:

            record = dict(row)

            # Use CGPA from the student profile
            record["Previous_CGPA"] = record["profile_cgpa"]

            risk, reasons = assess_risk(record)

            risks.append(risk)

            try:
                attendance = float(record["attendance"])

                if 0 <= attendance <= 100:
                    attendances.append(attendance)

            except (TypeError, ValueError):
                pass

        return {
            "total": total,
            "cgpa": cgpa,
            "attendance": (
                sum(attendances) / len(attendances)
                if attendances else 0
            ),
            "support": sum(
                risk in ("Moderate", "High")
                for risk in risks
            )
        }

    finally:
        c.close()


# --------------------------------------------------
# 5. SAVE STUDENT INTERVENTION
# --------------------------------------------------

def save_intervention(sid, uid, action, status):

    c = get_connection()

    try:
        c.execute(
            """
            INSERT INTO interventions
            (student_id, faculty_user_id, action, status)
            VALUES (?, ?, ?, ?)
            """,
            (sid, uid, action, status)
        )

        c.commit()

    finally:
        c.close()


# --------------------------------------------------
# 6. GET STUDENT INTERVENTIONS
# --------------------------------------------------

def get_interventions(sid):

    c = get_connection()

    try:
        rows = c.execute(
            """
            SELECT action, status, created_at
            FROM interventions
            WHERE student_id=?
            ORDER BY id DESC
            """,
            (sid,)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        c.close()


# --------------------------------------------------
# 7. ADD ACADEMIC RECORD
# --------------------------------------------------

def add_academic_record(row):

    c = get_connection()

    try:
        sid = str(row["Student_ID"]).strip()

        existing = c.execute(
            "SELECT student_id FROM students WHERE student_id=?",
            (sid,)
        ).fetchone()

        if not existing:

            c.execute(
                """
                INSERT INTO students
                (student_id, name, department, semester, previous_cgpa)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    sid,
                    str(row.get("Name", sid)),
                    str(row.get("Department", "Not specified")),
                    int(row.get("Semester", 1)),
                    float(row["Previous_CGPA"])
                )
            )

        subject = str(row.get("Subject", "General"))

        found = c.execute(
            "SELECT id FROM subjects WHERE subject_name=?",
            (subject,)
        ).fetchone()

        if found:
            subject_id = found["id"]

        else:
            cur = c.execute(
                """
                INSERT INTO subjects(subject_name, semester)
                VALUES (?, ?)
                """,
                (
                    subject,
                    int(row.get("Semester", 1))
                )
            )

            subject_id = cur.lastrowid

        c.execute(
            """
            INSERT INTO academic_records
            (
                student_id,
                subject_id,
                attendance,
                internal_marks,
                assignment_marks,
                quiz_marks,
                study_hours,
                previous_cgpa,
                backlogs,
                final_marks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sid,
                subject_id,
                float(row["Attendance"]),
                float(row["Internal_Marks"]),
                float(row["Assignment_Marks"]),
                float(row["Quiz_Marks"]),
                float(row["Study_Hours"]),
                float(row["Previous_CGPA"]),
                int(row["Backlogs"]),
                float(row["Final_Marks"])
            )
        )

        c.execute(
            """
            INSERT INTO marks
            (student_id, subject_id, assessment_type, score, max_score)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                sid,
                subject_id,
                "Final",
                float(row["Final_Marks"]),
                100
            )
        )

        c.execute(
            """
            INSERT INTO attendance
            (student_id, subject_id, attendance_percent)
            VALUES (?, ?, ?)
            """,
            (
                sid,
                subject_id,
                float(row["Attendance"])
            )
        )

        c.commit()

    except Exception:
        c.rollback()
        raise

    finally:
        c.close()


# --------------------------------------------------
# 8. LOG AUDIT EVENT
# --------------------------------------------------

def log_event(uid, event, detail):

    c = get_connection()

    try:
        c.execute(
            """
            INSERT INTO audit_log(user_id, event, detail)
            VALUES (?, ?, ?)
            """,
            (uid, event, detail)
        )

        c.commit()

    finally:
        c.close()
