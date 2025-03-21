import smtplib
from email.mime.text import MIMEText

def send_booking_confirmation(email, room, date, time):
    msg = MIMEText(f"Booking Anda telah dikonfirmasi!\nRuangan: {room}\nTanggal: {date}\nJam: {time}")
    msg["Subject"] = "Konfirmasi Booking Ruangan"
    msg["From"] = "admin@perpus.com"
    msg["To"] = email

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("admin@perpus.com", "password")
        server.sendmail("admin@perpus.com", [email], msg.as_string())
