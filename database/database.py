import sqlite3,hashlib
from pathlib import Path
DB_PATH=Path(__file__).resolve().parent/"trekverse.db"
def get_connection():
    c=sqlite3.connect(DB_PATH,check_same_thread=False);c.row_factory=sqlite3.Row;c.execute("PRAGMA foreign_keys=ON");return c
def _hash(p):return hashlib.sha256(p.encode()).hexdigest()
def init_db():
    c=get_connection()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,full_name TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN('admin','faculty','student')),student_id TEXT,active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS students(student_id TEXT PRIMARY KEY,name TEXT NOT NULL,department TEXT,semester INTEGER,previous_cgpa REAL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS subjects(id INTEGER PRIMARY KEY AUTOINCREMENT,subject_name TEXT NOT NULL,semester INTEGER);
    CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,subject_id INTEGER,attendance_percent REAL,recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(student_id) REFERENCES students(student_id),FOREIGN KEY(subject_id) REFERENCES subjects(id));
    CREATE TABLE IF NOT EXISTS marks(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,subject_id INTEGER,assessment_type TEXT,score REAL,max_score REAL,recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(student_id) REFERENCES students(student_id),FOREIGN KEY(subject_id) REFERENCES subjects(id));
    CREATE TABLE IF NOT EXISTS assignments(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,subject_id INTEGER,title TEXT,score REAL,max_score REAL,submitted INTEGER DEFAULT 0,due_date TEXT,FOREIGN KEY(student_id) REFERENCES students(student_id));
    CREATE TABLE IF NOT EXISTS academic_records(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,subject_id INTEGER,attendance REAL,internal_marks REAL,assignment_marks REAL,quiz_marks REAL,study_hours REAL,previous_cgpa REAL,backlogs INTEGER,final_marks REAL,recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(student_id) REFERENCES students(student_id),FOREIGN KEY(subject_id) REFERENCES subjects(id));
    CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,predicted_score REAL,risk_band TEXT,model_version TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(student_id) REFERENCES students(student_id));
    CREATE TABLE IF NOT EXISTS recommendations(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,recommendation TEXT,status TEXT DEFAULT 'Open',created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(student_id) REFERENCES students(student_id));
    CREATE TABLE IF NOT EXISTS interventions(id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,faculty_user_id INTEGER,action TEXT NOT NULL,status TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,event TEXT,detail TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    """)
    c.commit();c.close()
def seed_demo_data():
    c=get_connection()
    if c.execute("SELECT COUNT(*) FROM students").fetchone()[0]==0:
        c.executemany("INSERT OR IGNORE INTO users(username,password_hash,full_name,role,student_id) VALUES(?,?,?,?,?)",[
          ("admin",_hash("Admin@123"),"TREKVERSE Administrator","admin",None),
          ("faculty",_hash("Faculty@123"),"Demo Faculty","faculty",None),
          ("student",_hash("Student@123"),"Demo Student","student","STU1001")])
        rows=[
        ("STU1001","Aarav Kumar","CSE",5,7.2,78,72,68,75,2.5,7.2,0,76,"DBMS"),
        ("STU1002","Ananya Rao","CSE",5,8.3,94,88,91,90,3.5,8.3,0,89,"Programming"),
        ("STU1003","Rohan Das","IT",5,6.3,61,54,58,60,1.5,6.3,2,57,"Mathematics"),
        ("STU1004","Meera Nair","IT",5,7.7,84,79,82,80,3.0,7.7,0,82,"DBMS"),
        ("STU1005","Ishaan Reddy","ECE",5,6.9,70,65,61,67,2.0,6.9,1,66,"Electronics"),
        ("STU1006","Sana Ali","CSE",5,8.9,97,94,96,93,4.0,8.9,0,95,"Programming")]
        for sid,name,dept,sem,cgpa,att,im,am,qm,hrs,prev,back,final,sub in rows:
            cur=c.execute("INSERT INTO students(student_id,name,department,semester,previous_cgpa) VALUES(?,?,?,?,?)",(sid,name,dept,sem,cgpa))
            subrow=c.execute("SELECT id FROM subjects WHERE subject_name=?",(sub,)).fetchone()
            subject_id=subrow["id"] if subrow else c.execute("INSERT INTO subjects(subject_name,semester) VALUES(?,?)",(sub,sem)).lastrowid
            c.execute("""INSERT INTO academic_records(student_id,subject_id,attendance,internal_marks,assignment_marks,quiz_marks,study_hours,previous_cgpa,backlogs,final_marks) VALUES(?,?,?,?,?,?,?,?,?,?)""",
              (sid,subject_id,att,im,am,qm,hrs,prev,back,final))
            c.execute("INSERT INTO attendance(student_id,subject_id,attendance_percent) VALUES(?,?,?)",(sid,subject_id,att))
            c.execute("INSERT INTO marks(student_id,subject_id,assessment_type,score,max_score) VALUES(?,?,?,?,?)",(sid,subject_id,"Final",final,100))
        c.commit()
    c.close()
