import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from database import get_db, Booking, BookingStatus, Admin
from google_calendar.calendar_service import check_availability, create_event
from config import Config
from datetime import datetime
from email_service.send_email import send_booking_notification
from werkzeug.security import check_password_hash

ADMIN_EMAIL = "boydeviano75@gmail.com"

app = Flask(__name__)
app.config.from_object(Config)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))
    with get_db() as db:
        bookings = db.query(Booking).order_by(Booking.tanggal, Booking.jam).all()
    return render_template("admin.html", bookings=bookings)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        with get_db() as db:
            admin = db.query(Admin).filter_by(email=email).first()
            if admin and check_password_hash(admin.password, password):
                session["admin"] = admin.email
                flash("Login berhasil!", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Email atau password salah!", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Anda telah logout.", "info")
    return redirect(url_for("login"))

@app.route("/get_available_times", methods=["GET"])
def get_available_times():
    ruangan = request.args.get("ruangan")
    tanggal = request.args.get("tanggal")

    if not ruangan or not tanggal:
        return jsonify({"error": "Ruangan dan tanggal harus dipilih."}), 400

    jam_list = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]

    with get_db() as db:
        booked_times = db.query(Booking.jam).filter(
            Booking.ruangan == ruangan,
            Booking.tanggal == datetime.strptime(tanggal, "%Y-%m-%d").date(),
            Booking.status == BookingStatus.CONFIRMED
        ).all()
    
    booked_times = {jam[0] for jam in booked_times}
    
    available_times = [{"waktu": jam, "available": jam not in booked_times} for jam in jam_list]
    
    return jsonify({"jam": available_times})

@app.route("/booking", methods=["POST"])
def booking():
    try:
        nama = request.form["nama"].strip()
        nim = request.form["nim"].strip()
        email = request.form["email"].strip()
        ruangan = request.form["ruangan"].strip()
        tanggal = datetime.strptime(request.form["tanggal"], "%Y-%m-%d").date()
        waktu = request.form["waktu"].strip()
        jumlah_orang = int(request.form.get("jumlah_orang", "1").strip())

        if not all([nama, nim, email, ruangan, waktu, jumlah_orang]):
            return jsonify({"error": "Semua data harus diisi!"}), 400

        with get_db() as db:
            new_booking = Booking(
                nama=nama, nim=nim, email=email,
                ruangan=ruangan, tanggal=tanggal, jam=waktu,
                jumlah_orang=jumlah_orang, status=BookingStatus.PENDING
            )
            db.add(new_booking)
            db.commit()

        return jsonify({"message": "Booking berhasil! Menunggu konfirmasi admin.", "reset": True, "reset_time": True})
    except ValueError:
        return jsonify({"error": "Format tanggal atau jumlah orang salah!"}), 400


@app.route("/update_booking", methods=["POST"])
def update_booking():
    booking_id = request.form.get("booking_id")
    action = request.form.get("action")

    if not booking_id or action not in ["ACC", "CANCEL", "REJECT", "DELETE"]:
        return jsonify({"error": "Aksi tidak valid!"}), 400

    with get_db() as db:
        booking = db.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            return jsonify({"error": "Booking tidak ditemukan!"}), 404

        if action == "ACC":
            booking.status = BookingStatus.CONFIRMED
            create_event(booking.ruangan, booking.tanggal, booking.jam, booking.email, booking.jumlah_orang)
            send_booking_notification(booking.email, booking.ruangan, booking.tanggal, booking.jam, "Confirmed", booking.jumlah_orang)
        
        elif action == "CANCEL":
            booking.status = BookingStatus.CANCELLED

        elif action == "REJECT":
            booking.status = BookingStatus.REJECTED
            send_booking_notification(booking.email, booking.ruangan, booking.tanggal, booking.jam, "Rejected", booking.jumlah_orang)
            send_booking_notification(ADMIN_EMAIL, booking.ruangan, booking.tanggal, booking.jam, "Rejected", booking.jumlah_orang)
        
        elif action == "DELETE":
            db.delete(booking)
            db.commit()
            return jsonify({"message": "Booking berhasil dihapus.", "deleted": True})

        db.commit()

    return jsonify({"message": "Status booking diperbarui!"})

if __name__ == "__main__":
    app.run(debug=True)
