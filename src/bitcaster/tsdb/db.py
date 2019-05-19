from collections import OrderedDict

import pytz
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from redis import StrictRedis
from redis_timeseries import TimeSeries, days, hours, minutes, seconds


class TS(TimeSeries):
    def get_data(self, organization, data_type, granularity='m'):
        key = '%s:%s' % (organization, data_type)
        return self.get_buckets(key, granularity, 30)

    def log_channel_usage(self, channel):
        key = '%s:channel' % channel.id
        self.increase(key, 1)

    def log_error(self, organization):
        key = '%s:error' % organization.slug
        self.increase(key, 1)

    def log_occurence(self, organization):
        key = '%s:occurence' % organization.slug
        self.increase(key, 1)

    def log_notification(self, organization):
        key = '%s:notification' % organization.slug
        self.increase(key, 1)


granularities = OrderedDict([
    ('h', {'duration': minutes(1), 'ttl': minutes(60)}),
    ('d', {'duration': minutes(1), 'ttl': hours(24)}),
    ('m', {'duration': days(1), 'ttl': days(30)}),
    ('y', {'duration': days(1), 'ttl': days(365)}),
])


def get_stats():
    client = StrictRedis.from_url(settings.TSDB_STORE)
    return TS(client, base_key='stats', granularities=granularities, timezone=pytz.UTC)


stats = SimpleLazyObject(get_stats)

counters_granularities = OrderedDict([
    ('m', {'duration': seconds(60), 'ttl': minutes(1)}),
    ('h', {'duration': minutes(60), 'ttl': hours(1)}),
    ('d', {'duration': hours(24), 'ttl': days(1)}),
])


def get_counters():
    client = StrictRedis.from_url(settings.TSDB_STORE)
    return TS(client, base_key='counters',
              granularities=counters_granularities,
              timezone=pytz.UTC)


counters = SimpleLazyObject(get_counters)
