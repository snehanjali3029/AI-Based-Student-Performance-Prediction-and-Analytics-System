-- TREKVERSE relational schema. The same tables are initialized by database/database.py.
CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, full_name TEXT, role TEXT, student_id TEXT, active INTEGER);
CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT, department TEXT, semester INTEGER, previous_cgpa REAL);
CREATE TABLE subjects (id INTEGER PRIMARY KEY, subject_name TEXT, semester INTEGER);
CREATE TABLE attendance (id INTEGER PRIMARY KEY, student_id TEXT, subject_id INTEGER, attendance_percent REAL, recorded_at TEXT);
CREATE TABLE marks (id INTEGER PRIMARY KEY, student_id TEXT, subject_id INTEGER, assessment_type TEXT, score REAL, max_score REAL, recorded_at TEXT);
CREATE TABLE assignments (id INTEGER PRIMARY KEY, student_id TEXT, subject_id INTEGER, title TEXT, score REAL, max_score REAL, submitted INTEGER, due_date TEXT);
CREATE TABLE academic_records (id INTEGER PRIMARY KEY, student_id TEXT, subject_id INTEGER, attendance REAL, internal_marks REAL, assignment_marks REAL, quiz_marks REAL, study_hours REAL, previous_cgpa REAL, backlogs INTEGER, final_marks REAL, recorded_at TEXT);
CREATE TABLE predictions (id INTEGER PRIMARY KEY, student_id TEXT, predicted_score REAL, risk_band TEXT, model_version TEXT, created_at TEXT);
CREATE TABLE recommendations (id INTEGER PRIMARY KEY, student_id TEXT, recommendation TEXT, status TEXT, created_at TEXT);
CREATE TABLE interventions (id INTEGER PRIMARY KEY, student_id TEXT, faculty_user_id INTEGER, action TEXT, status TEXT, created_at TEXT);
CREATE TABLE audit_log (id INTEGER PRIMARY KEY, user_id INTEGER, event TEXT, detail TEXT, created_at TEXT);
