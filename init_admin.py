from database import get_db, Admin
from werkzeug.security import generate_password_hash

with get_db() as db:
    if not db.query(Admin).filter_by(email="Pradita Library").first():
        new_admin = Admin(email="Pradita Library", password=generate_password_hash("Pradita_Library75"))
        db.add(new_admin)
        db.commit()
        print("Admin berhasil ditambahkan!")
    else:
        print("Admin sudah ada!")
