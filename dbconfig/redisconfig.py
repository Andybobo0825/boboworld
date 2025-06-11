import redis
# 連接 Redis
cache = redis.StrictRedis(host='localhost', port=6379, db=0)

