import sqlite3
from database import get_db
from email_service.send_email import send_booking_notification
from google_calendar import create_event

# Definisikan email admin di sini
ADMIN_EMAIL = "boydeviano75@gmail.com"  # Ganti dengan alamat email admin yang valid

def check_availability(ruangan, tanggal, jam):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM bookings WHERE ruangan = ? AND tanggal = ? AND jam = ?
    """, (ruangan, tanggal, jam))
    result = cursor.fetchone()
    db.close()
    return result[0] == 0

def add_booking(nama, nim, email, ruangan, tanggal, jam, jumlah_orang):
    db = get_db()
    cursor = db.cursor()

    if not check_availability(ruangan, tanggal, jam):
        return {"error": "Ruangan sudah dibooking pada waktu tersebut."}

    try:
        cursor.execute("""
            INSERT INTO bookings (nama, nim, email, ruangan, tanggal, jam, jumlah_orang, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """, (nama, nim, email, ruangan, tanggal, jam, jumlah_orang))
        booking_id = cursor.lastrowid  
        db.commit()

        event_link = create_event(ruangan, tanggal, jam, email, jumlah_orang)

        if event_link:
            cursor.execute("""
                UPDATE bookings SET status = 'CONFIRMED' WHERE id = ?
            """, (booking_id,))
            db.commit()

            from flask import redirect, url_for
            return redirect(url_for('dashboard_admin')) 

        else:
            cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
            db.commit()
            return {"error": "Gagal membuat event di Google Calendar."}

    except Exception as e:
        db.rollback()
        return {"error": f"Gagal melakukan booking: {e}"}

    finally:
        db.close()

def reject_booking(booking_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE bookings SET status = 'REJECTED' WHERE id = ?", (booking_id,))
        db.commit()

        # Ambil email client berdasarkan booking_id
        cursor.execute("SELECT email, ruangan, tanggal, jam FROM bookings WHERE id = ?", (booking_id,))
        booking = cursor.fetchone()

        if booking:
            email, ruangan, tanggal, jam = booking
            send_booking_notification(email, ruangan, tanggal, jam, "Rejected")
            send_booking_notification(ADMIN_EMAIL, ruangan, tanggal, jam, "Rejected")  # Kirim ke admin juga

        return {"success": "Booking telah ditolak dan email sudah dikirim."}

    except Exception as e:
        db.rollback()
        return {"error": f"Gagal menolak booking: {e}"}

    finally:
        db.close()
