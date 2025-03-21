import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from dotenv import dotenv_values
from functools import lru_cache

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

config = dotenv_values(".env")

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = config.get("SERVICE_ACCOUNT_FILE")
CALENDAR_ID = config.get("CALENDAR_ID")

if not SERVICE_ACCOUNT_FILE:
    logging.error("SERVICE_ACCOUNT_FILE tidak dikonfigurasi.")
    raise FileNotFoundError("SERVICE_ACCOUNT_FILE tidak ditemukan di .env.")

if not CALENDAR_ID:
    logging.error("CALENDAR_ID belum dikonfigurasi di .env")
    raise ValueError("CALENDAR_ID belum dikonfigurasi.")

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
    logging.info("Google Calendar API berhasil diinisialisasi.")
except Exception as e:
    logging.error(f"Error saat menginisialisasi Google Calendar API: {e}")
    raise e

@lru_cache(maxsize=100)
def check_availability(room: str, date: str, time: str) -> bool:
    try:
        start_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S+07:00")

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time_str,
            timeMax=end_time_str,
            singleEvents=True,
            orderBy="startTime",
            maxResults=5  # Batasi hasil untuk mempercepat query
        ).execute()

        events = events_result.get("items", [])
        booked = any(event.get("summary", "").lower() == room.lower() for event in events)
        
        logging.info(f"Ruangan {room} {'tidak tersedia' if booked else 'tersedia'} pada {start_time_str}.")
        return not booked
    except HttpError as http_err:
        logging.error(f"HTTP Error saat mengecek ketersediaan: {http_err}")
        return False
    except Exception as e:
        logging.error(f"Error saat mengecek ketersediaan: {e}")
        return False

def create_event(room: str, date: str, time: str, email: str, jumlah_orang: int):
    """
    Membuat event booking di Google Calendar.
    """
    try:
        start_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S+07:00")

        event_body = {
            "summary": f"Booking {room} - {jumlah_orang} Orang",
            "description": f"Booking oleh {email}",
            "start": {"dateTime": start_time_str, "timeZone": "Asia/Jakarta"},
            "end": {"dateTime": end_time_str, "timeZone": "Asia/Jakarta"},
            "attendees": [{"email": email}]
        }

        event_created = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
        event_link = event_created.get("htmlLink")

        logging.info(f"Event berhasil dibuat: {event_link}")
        return event_link
    except HttpError as http_err:
        logging.error(f"HTTP Error saat membuat event: {http_err}")
        return None
    except Exception as e:
        logging.error(f"Error saat membuat event: {e}")
        return None
