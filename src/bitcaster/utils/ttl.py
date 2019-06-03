import re
from collections import defaultdict

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 30
YEAR = DAY * 365


def parse_ttl(ttl):
    """
    :param ttl:
    :return:

    >>> parse_ttl('1w')
    604800

    """
    durations = {'s': 1,
                 'm': 60,  # minute
                 'h': 3600,  # hour
                 'd': 86400,  # day
                 'w': 604800,  # week
                 'y': 31536000}  # year
    rex = re.compile(r'((\d+)([smhdwy]))')
    try:
        groups = rex.findall(ttl)
        if not groups:
            return int(ttl)
        return sum([int(g[1]) * durations[g[2]] for g in groups])
    except TypeError:
        return int(ttl)


def encode_ttl(value):
    values = defaultdict(lambda: 0, y=0, w=0, d=0, h=0, m=0, s=0)
    v = value
    while v > 0:
        if v < MINUTE:
            values['s'] = v
            v -= v
        elif v < HOUR:
            values['m'] = v // MINUTE
            v -= values['m'] * MINUTE
        elif v < DAY:
            values['h'] = v // HOUR
            v -= values['h'] * HOUR
        elif v < WEEK:
            values['d'] = v // DAY
            v -= values['d'] * DAY
        elif v < YEAR:
            values['w'] = v // WEEK
            v -= values['w'] * WEEK
        elif v >= YEAR:
            values['y'] = v // YEAR
            v -= values['y'] * YEAR
        else:
            v = 0
    ret = []
    for unit in ['y', 'w', 'd', 'h', 'm', 's']:
        if values[unit]:
            ret.append('%d%s' % (values[unit], unit))

    return ''.join(ret)
