import redis

r = redis.Redis(host='localhost', port=6379, db=0)
r.set("halo", "dunia")
print(r.get("halo").decode())
