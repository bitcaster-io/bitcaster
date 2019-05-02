import redis


class TSDBBase:
    def __init__(self):
        self.client = redis.StrictRedis(host='192.168.66.66', port=6379)


class TSDBNotification(TSDBBase):
    pass
