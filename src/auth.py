import hashlib
from database.database import get_connection

def authenticate(username,password):
    c=get_connection()
    row=c.execute("SELECT * FROM users WHERE username=? AND active=1",(username,)).fetchone()
    c.close()
    if row and hashlib.sha256(password.encode()).hexdigest()==row["password_hash"]:
        return dict(row)
    return None
