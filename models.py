from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
import enum

db = SQLAlchemy()

class BookingStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.String, primary_key=True)
    nama = db.Column(db.String, nullable=False)
    nim = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    ruangan = db.Column(db.String, nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    jam = db.Column(db.String, nullable=False)  
    durasi = db.Column(db.Integer, CheckConstraint("durasi > 0"), nullable=False)
    jumlah_orang = db.Column(db.Integer, CheckConstraint("jumlah_orang > 0"), nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)

    def __repr__(self):
        return (
            f"<Booking(id={self.id}, nama={self.nama}, ruangan={self.ruangan}, "
            f"tanggal={self.tanggal}, jam={self.jam}, durasi={self.durasi}, "
            f"jumlah_orang={self.jumlah_orang}, status={self.status})>"
        )

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

# Untuk testing mandiri
if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("✅ Tabel bookings dan admins berhasil dibuat.")
