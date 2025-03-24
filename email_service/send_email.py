import smtplib
from email.mime.text import MIMEText

ADMIN_EMAIL = "boydeviano75@gmail.com"
SENDER_EMAIL = "boydeviano75@gmail.com"  # Ganti dengan email pengirim yang valid
APP_PASSWORD = "mhse udae apmp whbg"  # Ganti dengan App Password yang benar

def send_booking_notification(email, room, date, time, status, jumlah_orang):
    # Pesan umum yang selalu ada di setiap email
    footer_message = (
        "\n\nTerima kasih telah menggunakan Pradita library Infrastructure Services, "
        "Gunakanlah ruangan secara bijak dan patuhi seluruh aturan yang berlaku.\n\n"
        "Best Regards,\nUnit Library."
    )

    if status == "Confirmed":
        subject = "Konfirmasi Booking Ruangan"
        body = (f"Booking Anda telah dikonfirmasi!\n\n"
                f"Ruangan: {room}\n"
                f"Tanggal: {date}\n"
                f"Jam: {time}\n"
                f"Jumlah Orang: {jumlah_orang}\n\n"  # Menambahkan jumlah orang
                "Terima kasih telah menggunakan Pradita library Infrastructure Services, "
                "Gunakanlah ruangan secara bijak dan patuhi seluruh aturan yang berlaku.\n\n"
                "Best Regards,\nUnit Library.")
    elif status == "Rejected":
        subject = "Booking Ruangan Ditolak"
        body = (f"Maaf, booking Anda telah ditolak.\n\n"
                f"Ruangan: {room}\n"
                f"Tanggal: {date}\n"
                f"Jam: {time}\n"
                f"Jumlah Orang: {jumlah_orang}\n\n"  # Menambahkan jumlah orang
                "Silakan Konsultasi dengan staff Library." + footer_message)  # Pesan footer tetap ada
    else:
        return  # Jika status tidak sesuai, hentikan fungsi
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, [email, ADMIN_EMAIL], msg.as_string())  # Kirim ke client & admin
        print(f"✅ Email terkirim ke {email} & {ADMIN_EMAIL}")
    except smtplib.SMTPAuthenticationError:
        print("❌ ERROR: Gagal login ke SMTP. Periksa kembali email & App Password!")
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Contoh panggilan fungsi untuk pengujian
send_booking_notification("client@example.com", "Ruangan A", "2025-03-30", "14:00", "Confirmed", 5)
send_booking_notification("client@example.com", "Ruangan A", "2025-03-30", "14:00", "Rejected", 5)
