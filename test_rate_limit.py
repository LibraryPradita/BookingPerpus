import requests
import time
from datetime import datetime

url = 'http://localhost:5000/admin'

for i in range(35):  # 35x request
    try:
        response = requests.get(url)
        now = datetime.now().strftime('%H:%M:%S')
        print(f"{i+1}: {now} - {response.status_code} - {response.text}")
    except Exception as e:
        print(f"{i+1}: ERROR - {e}")
    time.sleep(0.1)  # cuma 0.1 detik antar request
