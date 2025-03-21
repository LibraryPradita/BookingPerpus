import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import get_db, Booking, BookingStatus
from google_calendar.calendar_service import check_availability, create_event
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin_dashboard():
    with get_db() as db:
        bookings = db.query(Booking).order_by(Booking.tanggal, Booking.jam).all()
    return render_template("admin.html", bookings=bookings)

@app.route("/get_available_times", methods=["GET"])
def get_available_times():
    ruangan = request.args.get("ruangan")
    tanggal = request.args.get("tanggal")

    if not ruangan or not tanggal:
        return jsonify({"error": "Ruangan dan tanggal harus dipilih."}), 400

    jam_list = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
    available_times = []

    for jam in jam_list:
        available = check_availability(ruangan, tanggal, jam)
        available_times.append({"waktu": jam, "available": available})

    return jsonify({"jam": available_times})

@app.route("/booking", methods=["POST"])
def booking():
    nama = request.form.get("nama", "").strip()
    nim = request.form.get("nim", "").strip()
    email = request.form.get("email", "").strip()
    ruangan = request.form.get("ruangan", "").strip()
    tanggal_str = request.form.get("tanggal", "").strip()
    waktu = request.form.get("waktu", "").strip()
    jumlah_orang = request.form.get("jumlah_orang", "1").strip()

    if not all([nama, nim, email, ruangan, tanggal_str, waktu, jumlah_orang]):
        return jsonify({"error": "Semua data harus diisi!"}), 400

    try:
        tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()
        jumlah_orang = int(jumlah_orang)
    except ValueError:
        return jsonify({"error": "Format tanggal atau jumlah orang salah!"}), 400

    with get_db() as db:
        new_booking = Booking(
            nama=nama, nim=nim, email=email,
            ruangan=ruangan, tanggal=tanggal, jam=waktu,
            jumlah_orang=jumlah_orang, status=BookingStatus.PENDING
        )
        db.add(new_booking)
        db.commit()

    return jsonify({"message": "Booking berhasil! Menunggu konfirmasi admin."})


@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():
    nama = request.form.get("nama", "").strip()
    nim = request.form.get("nim", "").strip()
    email = request.form.get("email", "").strip()
    ruangan = request.form.get("ruangan", "").strip()
    tanggal_str = request.form.get("tanggal", "").strip()
    waktu = request.form.get("waktu", "").strip()
    jumlah_orang = request.form.get("jumlah_orang", "1").strip()

    try:
        tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()
        jumlah_orang = int(jumlah_orang)
    except ValueError:
        flash("Format tanggal atau jumlah orang salah!", "error")
        return redirect(url_for("home"))

    with get_db() as db:
        new_booking = Booking(
            nama=nama, nim=nim, email=email,
            ruangan=ruangan, tanggal=tanggal, jam=waktu,
            jumlah_orang=jumlah_orang, status=BookingStatus.PENDING
        )
        db.add(new_booking)
        db.commit()

    flash("Booking berhasil! Menunggu konfirmasi admin.", "success")
    return redirect(url_for("home"))

@app.route("/update_booking", methods=["POST"])
def update_booking():
    booking_id = request.form.get("booking_id")
    action = request.form.get("action")

    if not booking_id or action not in ["ACC", "CANCEL", "REJECT"]:
        return jsonify({"error": "Aksi tidak valid!"}), 400

    with get_db() as db:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return jsonify({"error": "Booking tidak ditemukan!"}), 404

        if action == "ACC":
            booking.status = BookingStatus.CONFIRMED
            create_event(booking.ruangan, booking.tanggal, booking.jam, booking.email, booking.jumlah_orang)
        elif action == "CANCEL":
            booking.status = BookingStatus.CANCELLED
        elif action == "REJECT":
            db.delete(booking)

        db.commit()

    return jsonify({"message": "Status booking diperbarui!"})

if __name__ == "__main__":
    app.run(debug=True)
