import uuid
import os 
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, session
)
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy

from config import Config
from database import Booking, BookingStatus, Admin
from models import db
from init_db import init_database
from google_calendar.calendar_service import check_availability, create_event
from email_service.send_email import send_booking_notification
from security.rate_limiter import limit_admin_requests

ADMIN_EMAIL = "boydeviano75@gmail.com"

app = Flask(__name__)
app.config.from_object(Config)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

db.init_app(app)
init_database()

# Middleware rate limiter
@app.before_request
def before_request():
    if request.path.startswith("/admin"):
        limit_admin_requests()

# Admin login decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            flash("⚠ Anda harus login sebagai admin.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
@admin_required
def admin_dashboard():
    bookings = db.session.query(Booking).order_by(Booking.tanggal.desc(), Booking.jam).all()
    return render_template("admin.html", bookings=bookings)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        admin = db.session.query(Admin).filter_by(email=email).first()

        if admin and check_password_hash(admin.password, password):
            session["admin"] = admin.email
            flash("✅ Login berhasil!", "success")
            return redirect(url_for("admin_dashboard"))
        flash("❌ Email atau password salah!", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("ℹ️ Anda telah logout.", "info")
    return redirect(url_for("login"))

@app.route("/get_available_times", methods=["GET"])
def get_available_times():
    ruangan = request.args.get("ruangan")
    tanggal = request.args.get("tanggal")

    if not ruangan or not tanggal:
        return jsonify({"error": "Ruangan dan tanggal harus dipilih."}), 400

    try:
        tanggal_obj = datetime.strptime(tanggal, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Format tanggal tidak valid. Gunakan format YYYY-MM-DD."}), 400

    jam_list = [f"{hour:02}:00" for hour in range(8, 17)]
    bookings = db.session.query(Booking).filter_by(
        ruangan=ruangan,
        tanggal=tanggal_obj,
        status=BookingStatus.CONFIRMED
    ).all()

    blocked = set()
    for booking in bookings:
        start_hour = int(booking.jam.split(":")[0])
        for i in range(booking.durasi):
            blocked.add(f"{start_hour + i:02}:00")

    available_times = [{"waktu": jam, "available": jam not in blocked} for jam in jam_list]
    return jsonify({"jam": available_times})

@app.route("/booking", methods=["POST"])
def create_booking():
    data = request.get_json()
    try:
        tanggal = datetime.strptime(data["tanggal"], "%Y-%m-%d").date()
        booking = Booking(
            id=str(uuid.uuid4()),
            nama=data["nama"],
            nim=data["nim"],
            email=data["email"],
            ruangan=data["ruangan"],
            tanggal=tanggal,
            jam=data["jam"],
            jumlah_orang=int(data["jumlah_orang"]),
            durasi=int(data["durasi"]),
            status=BookingStatus.PENDING
        )
        db.session.add(booking)
        db.session.commit()
        return jsonify({"success": True, "message": "📅 Booking berhasil!"})
    except (ValueError, KeyError) as e:
        print("Input error:", e)
        return jsonify({"success": False, "message": "Format data tidak valid."}), 400
    except Exception as e:
        print("Error saat booking:", e)
        return jsonify({"success": False, "message": "Terjadi kesalahan saat menyimpan booking."}), 500

@app.route("/update_booking", methods=["POST"])
@admin_required
def update_booking():
    booking_id = request.form.get("booking_id")
    action = request.form.get("action")

    if not booking_id or action not in ["ACC", "CANCEL", "REJECT", "DELETE"]:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "error", "message": "Aksi tidak valid!"}), 400
        flash("⚠ Aksi tidak valid!", "danger")
        return redirect(url_for("admin_dashboard"))

    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    if not booking:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "error", "message": "Booking tidak ditemukan!"}), 404
        flash("❌ Booking tidak ditemukan!", "danger")
        return redirect(url_for("admin_dashboard"))

    try:
        msg = ""
        status = "success"

        if action == "ACC":
            if booking.status != BookingStatus.PENDING:
                msg = "Booking hanya bisa dikonfirmasi dari status PENDING."
                status = "warning"
            elif db.session.query(Booking).filter(
                Booking.id != booking.id,
                Booking.ruangan == booking.ruangan,
                Booking.tanggal == booking.tanggal,
                Booking.jam == booking.jam,
                Booking.status == BookingStatus.CONFIRMED
            ).first():
                msg = "Ruangan sudah dibooking pada jam & tanggal tersebut!"
                status = "warning"
            else:
                booking.status = BookingStatus.CONFIRMED
                create_event(booking.ruangan, booking.tanggal, booking.jam, booking.email, booking.jumlah_orang)
                send_booking_notification(booking.email, booking.ruangan, booking.tanggal, booking.jam, "Confirmed", booking.jumlah_orang)
                msg = "Booking berhasil dikonfirmasi."

        elif action == "CANCEL":
            booking.status = BookingStatus.CANCELLED
            send_booking_notification(booking.email, booking.ruangan, booking.tanggal, booking.jam, "Cancelled", booking.jumlah_orang)
            msg = "Booking telah dibatalkan."
            status = "warning"

        elif action == "REJECT":
            if booking.status != BookingStatus.PENDING:
                msg = "Booking hanya bisa ditolak dari status PENDING."
                status = "warning"
            else:
                booking.status = BookingStatus.REJECTED
                send_booking_notification(booking.email, booking.ruangan, booking.tanggal, booking.jam, "Rejected", booking.jumlah_orang)
                send_booking_notification(ADMIN_EMAIL, booking.ruangan, booking.tanggal, booking.jam, "Rejected", booking.jumlah_orang)
                msg = "Booking telah ditolak."
                status = "danger"

        elif action == "DELETE":
            db.session.delete(booking)
            msg = "Booking telah dihapus."
            status = "success"

        db.session.commit()

        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": status, "message": msg})

    except Exception as e:
        db.session.rollback()
        print("[ERROR]", e)
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "error", "message": f"Terjadi error: {str(e)}"}), 500
        flash(f"❗ Terjadi error saat memproses booking: {str(e)}", "danger")

    return redirect(url_for("admin_dashboard"))
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
