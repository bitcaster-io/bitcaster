from collections import OrderedDict

import redis
from django.conf import settings
from redis_timeseries import TimeSeries, days, hours, minutes

EVENT = 'event'
NOTIFICATION = 'notification'
OCCURENCE = 'occurence'

MINUTE = '1minute'
HOUR = '1hour'
DAY = '1day'

granularities = OrderedDict([
    # ('1minute', {'duration': minutes(1), 'ttl': hours(1)}),
    # ('5minute', {'duration': minutes(5), 'ttl': hours(6)}),
    ('15minute', {'duration': minutes(15), 'ttl': hours(24)}),
    ('1hour', {'duration': hours(1), 'ttl': days(7)}),
    ('1day', {'duration': days(1), 'ttl': days(31)}),
])


class BcTimeSeries(TimeSeries):
    def __init__(self, broker, organization_pk):
        super().__init__(broker.client, str(organization_pk), granularities=granularities)

    def log_occurence(self, event):
        """
        log event occurence. ie event triggered by external application

        :param status: status of event (Event.status)
        :return:
        """
        self.increase(EVENT, 1)

    def log_notification(self, notification):
        """
        log event notification to recipient.

        :param status: status of event (Event.status)
        :return:
        """
        self.increase(NOTIFICATION, 1)
        # ts.record_hit(EVENT)
        # assert ts.get_hits(EVENT, MINUTE, 3)


class TSDBBroker:
    def __init__(self, url):
        self.client = redis.StrictRedis.from_url(url)

    def get_ts(self, organization_slug):
        return BcTimeSeries(self, organization_slug)


broker = TSDBBroker(settings.TSDB_STORE)
