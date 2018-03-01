class RateLimiter(object):
    window = 60

    def is_limited(self, key, limit, project=None, window=None):
        return False
