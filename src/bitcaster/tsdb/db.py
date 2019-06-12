# Errors
#   error:org:<org.pk>
#   error:ch:<channel.pk>
#   error:evt:<event.pk>
#   error:sub:<subscription.pk>

# Occurence
#   occurence:org:<org.pk>

# Notifications:
#   notification:org:<org.pk>
#   notification:ch:<channel.pk>
#   notification:sub:<subscription.pk>
#   notification:evt:<event.pk>

# Buffers:
#   buffer:org:<org.pk>
#   buffer:ch:<channel.pk>
#   buffer:evt:<event.pk>

# Confirmations:
#   confirmation:org:<org.pk>
#   confirmation:evt:<event.pk>

import calendar
import functools
import operator
from collections import OrderedDict
from datetime import datetime

import pytz

__all__ = ['TimeSeries', 'seconds', 'minutes', 'hours', 'days']

seconds = lambda i: i
minutes = lambda i: i * seconds(60)
hours = lambda i: i * minutes(60)
days = lambda i: i * hours(24)


class TimeSeries:
    granularities = OrderedDict([
        ('h', {'duration': minutes(1), 'ttl': minutes(60)}),
        ('d', {'duration': minutes(1), 'ttl': hours(24)}),
        ('m', {'duration': days(1), 'ttl': days(30)}),
        ('y', {'duration': days(1), 'ttl': days(365)}),
    ])

    # granularities = OrderedDict([
    #     ('1minute', {'duration': minutes(1), 'ttl': hours(1)}),
    #     ('5minute', {'duration': minutes(5), 'ttl': hours(6)}),
    #     ('10minute', {'duration': minutes(10), 'ttl': hours(12)}),
    #     ('1hour', {'duration': hours(1), 'ttl': days(7)}),
    #     ('1day', {'duration': days(1), 'ttl': days(31)}),
    # ])

    def __init__(self, client, base_key='stats', timezone=None, granularities=None):
        self.client = client
        self.base_key = base_key
        self.timezone = timezone
        self.granularities = granularities or self.granularities

    @property
    def chain(self):
        if self._chain is None:
            self._chain = self.client.pipeline()
        return self._chain

    @chain.setter
    def chain(self, value):
        self._chain = value

    def get_key(self, key, timestamp, granularity):
        ttl = self.granularities[granularity]['ttl']
        timestamp_key = round_time(timestamp, ttl)  # No timezone offset in the key
        return ':'.join([self.base_key, granularity, str(timestamp_key), str(key)])

    def add(self, key, type='counter', amount=1, execute=True):
        pipe = self.client.pipeline() if execute else self.chain
        pipe.incrby('%s:%s' % (key, type), amount)

        if execute:
            pipe.execute()

    def rm(self, key, type='counter', amount=1, execute=True):
        pipe = self.client.pipeline() if execute else self.chain
        pipe.decrby('%s:%s' % (key, type), amount)

        if execute:
            pipe.execute()

    def set(self, key, amount=1, execute=True):
        pipe = self.client.pipeline() if execute else self.chain
        pipe.set(key, amount)

        if execute:
            pipe.execute()

    def get_data(self, key):
        # k = '%s:counter' % key
        # TODO: remove me
        print(111, 'db.py:102', 1111111, key)
        ret = self.client.get(key)
        return ret or b'0'

    def increase(self, key, amount=1, timestamp=None, execute=True):
        pipe = self.client.pipeline() if execute else self.chain

        for granularity, props in self.granularities.items():
            hkey = self.get_key(key, timestamp, granularity)
            bucket = round_time_with_tz(timestamp, props['duration'], self.timezone)
            pipe.hincrby(hkey, bucket, amount)

            pipe.expire(hkey, props['ttl'])

        if execute:
            pipe.execute()

    def decrease(self, key, amount=1, timestamp=None, execute=True):
        self.increase(key, -1 * amount, timestamp, execute)

    def execute(self):
        results = self.chain.execute()
        self.chain = None
        return results

    def get_buckets(self, key, granularity, count=None, timestamp=None):
        if count is None:
            props = self.granularities[granularity]
            count = props['ttl'] // props['duration']
        else:
            props = self.granularities[granularity]
            if count > (props['ttl'] / props['duration']):
                raise ValueError('Count exceeds granularity limit')

        pipe = self.client.pipeline()
        buckets = []
        rounded = round_time_with_tz(timestamp, props['duration'], self.timezone)
        bucket = rounded - (count * props['duration'])

        for _ in range(count):
            bucket += props['duration']
            buckets.append(unix_to_dt(bucket))
            pipe.hget(self.get_key(key, bucket, granularity), bucket)

        parse = lambda x: int(x or 0)

        results = map(parse, pipe.execute())

        return list(zip(buckets, results))

    def get_total(self, *args, **kwargs):
        return sum([
            amount for bucket, amount in self.get_buckets(*args, **kwargs)
        ])

    def scan_keys(self, granularity, count, search='*', timestamp=None):
        props = self.granularities[granularity]
        if count > (props['ttl'] / props['duration']):
            raise ValueError('Count exceeds granularity limit')

        hkeys = set()
        prefixes = set()
        rounded = round_time_with_tz(timestamp, props['duration'], self.timezone)
        bucket = rounded - (count * props['duration'])

        for _ in range(count):
            bucket += props['duration']
            hkeys.add(self.get_key(search, bucket, granularity))
            prefixes.add(self.get_key('', bucket, granularity))

        pipe = self.client.pipeline()
        for key in hkeys:
            pipe.keys(key)
        results = functools.reduce(operator.add, pipe.execute())

        parsed = set()
        for result in results:
            result = result.decode('utf-8')
            for prefix in prefixes:
                result = result.replace(prefix, '')
            parsed.add(result)

        return sorted(parsed)


def round_time(dt, precision):
    seconds = dt_to_unix(dt or tz_now())
    return int((seconds // precision) * precision)


def round_time_with_tz(dt, precision, tz=None):
    rounded = round_time(dt, precision)

    if tz and precision % days(1) == 0:
        rounded_dt = unix_to_dt(rounded).replace(tzinfo=None)
        offset = tz.utcoffset(rounded_dt).total_seconds()
        rounded = int(rounded - offset)

        dt = unix_to_dt(dt or tz_now())
        dt_seconds = (hours(dt.hour) + minutes(dt.minute) + seconds(dt.second))
        if offset < 0 and dt_seconds < abs(offset):
            rounded -= precision
        elif offset > 0 and dt_seconds >= days(1) - offset:
            rounded += precision

    return rounded


def tz_now():
    if pytz:
        return datetime.utcnow().replace(tzinfo=pytz.utc)
    else:
        return datetime.now()


def dt_to_unix(dt):
    if isinstance(dt, datetime):
        dt = calendar.timegm(dt.utctimetuple())
    return dt


def unix_to_dt(dt):
    if isinstance(dt, (int, float)):
        utc = pytz.utc if pytz else None
        try:
            dt = datetime.fromtimestamp(dt, utc)
        except ValueError:
            dt = datetime.fromtimestamp(dt / 1000., utc)
    return dt
