import redis
from redis_timeseries import TimeSeries, days, hours, minutes

from bitcaster.config.environ import env


class TSDBBase:
    pass


class TSDBMemory(TSDBBase):
    pass


def test_tsdb():
    EVENT = 'event:1'
    MINUTE = '1minute'
    HOUR = '1hour'
    DAY = '1day'
    client = redis.StrictRedis.from_url(env('REDIS_TSDB_URL'))
    my_granularities = {
        MINUTE: {'ttl': hours(1), 'duration': minutes(1)},
        HOUR: {'ttl': days(7), 'duration': hours(1)},
        DAY: {'ttl': days(30), 'duration': days(1)},
    }
    ts = TimeSeries(client, base_key='my_timeseries', granularities=my_granularities)

    ts.record_hit(EVENT)
    assert ts.get_hits(EVENT, MINUTE, 3)
