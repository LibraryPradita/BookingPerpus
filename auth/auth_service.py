from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, Admin

def hash_password(password):
    return generate_password_hash(password)

def verify_admin(email, password):
    with get_db() as db:
        admin = db.query(Admin).filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            return admin
    return None
