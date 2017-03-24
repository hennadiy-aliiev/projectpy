import time
from datetime import datetime

from app import app, redis


def mark_online(id):
    now = int(time.time())
    expires = now + (app.config['ONLINE_LAST_MINUTES'] * 60) + 10
    all_users_key = 'online-users/{}'.format(now // 60)
    user_key = 'user-activity/{}'.format(id)
    p = redis.pipeline()
    p.sadd(all_users_key, id)
    p.set(user_key, now)
    p.expireat(all_users_key, expires)
    p.expireat(user_key, expires)
    p.execute()

def get_user_last_activity(id):
    last_active = redis.get('user-activity/{}'.format(id))
    if last_active is None:
        return None
    return datetime.utcfromtimestamp(int(last_active))

def get_online_users():
    current = int(time.time()) // 60
    minutes = range(app.config['ONLINE_LAST_MINUTES'])
    return redis.sunion(['online-users/{}'.format(current - x) for x in minutes])
