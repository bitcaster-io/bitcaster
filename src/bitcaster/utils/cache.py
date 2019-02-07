from bitcaster import get_full_version
from bitcaster.config import settings


def make_key(key, key_prefix, version):
    if settings.DEBUG:
        import time
        return ':'.join([key_prefix, str(version), str(time.time()), key])
    return ':'.join([key_prefix, str(version), get_full_version(), key])
