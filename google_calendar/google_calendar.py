import logging
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from dotenv import dotenv_values
from functools import lru_cache

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Memuat variabel lingkungan dari .env
config = dotenv_values(".env")

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = config.get("SERVICE_ACCOUNT_FILE")
CALENDAR_ID = config.get("CALENDAR_ID")

# Validasi kredensial
if not SERVICE_ACCOUNT_FILE or not CALENDAR_ID:
    logging.error("Konfigurasi SERVICE_ACCOUNT_FILE atau CALENDAR_ID tidak ditemukan.")
    raise ValueError("Pastikan SERVICE_ACCOUNT_FILE dan CALENDAR_ID sudah diatur di .env")

# Inisialisasi Google Calendar API
try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=credentials)
    logging.info("Google Calendar API berhasil diinisialisasi.")
except Exception as e:
    logging.error(f"Error saat inisialisasi Google Calendar API: {e}")
    raise e

# Caching menggunakan lru_cache untuk menghindari request API berulang
@lru_cache(maxsize=100)
def check_availability(room: str, date: str, time: str) -> bool:
    """
    Mengecek apakah ruangan tersedia berdasarkan tanggal dan waktu yang diberikan.
    """

    start_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    end_time = start_time + timedelta(hours=1)

    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S+07:00")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S+07:00")

    try:
        # Benchmark waktu eksekusi
        start_exec_time = time.time()

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time_str,
            timeMax=end_time_str,
            singleEvents=True,
            orderBy="startTime",
            maxResults=5  # Batasi jumlah hasil agar lebih cepat
        ).execute()

        events = events_result.get("items", [])

        # Optimasi pencarian booking ruangan
        booked = any(event.get("summary", "").strip().lower() == room.lower() for event in events)

        logging.info(f"Ruangan {room} {'sudah dibooking' if booked else 'tersedia'} pada {start_time_str}.")

        end_exec_time = time.time()
        logging.info(f"Waktu eksekusi check_availability: {end_exec_time - start_exec_time:.2f} detik")

        return not booked

    except HttpError as http_err:
        logging.error(f"HTTP Error saat mengecek ketersediaan: {http_err}")
        return False
    except Exception as e:
        logging.error(f"Error saat mengecek ketersediaan: {e}")
        return False
