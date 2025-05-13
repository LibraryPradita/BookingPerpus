import time
import redis
from flask import request, abort

# Koneksi ke Redis (default: localhost:6379)
r = redis.Redis(host='localhost', port=6379, db=0)

MAX_REQUEST = 30
TIME_WINDOW = 60  # detik

def limit_admin_requests():
    if request.path.startswith('/admin'):
        ip = request.remote_addr
        key = f"rl:{ip}"
        now = int(time.time())

        # Gunakan pipeline Redis untuk efisiensi
        with r.pipeline() as pipe:
            pipe.zadd(key, {str(now): now})
            pipe.zremrangebyscore(key, 0, now - TIME_WINDOW)
            pipe.zcard(key)
            pipe.expire(key, TIME_WINDOW)
            _, _, request_count, _ = pipe.execute()

        print(f"[RateLimiter] IP: {ip}, Requests: {request_count}")  # Optional log

        if request_count > MAX_REQUEST:
            abort(429, description="Terlalu banyak request ke halaman admin.")
