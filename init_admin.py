from models import db
from database import Admin  # Kalau Admin ada di database.py
from werkzeug.security import generate_password_hash
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

    if not db.session.query(Admin).filter_by(email="Pradita Library").first():
        new_admin = Admin(
            email="Pradita Library",
            password=generate_password_hash("Pradita_Library75")
        )
        db.session.add(new_admin)
        db.session.commit()
        print("Admin berhasil ditambahkan!")
    else:
        print("Admin sudah ada!")
