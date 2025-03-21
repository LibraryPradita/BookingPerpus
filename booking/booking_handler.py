import sqlite3
from database import get_db
from email_service.send_email import send_email
from google_calendar import create_event

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
