from collections import OrderedDict

import pytz
import redis
from redis_timeseries import TimeSeries, days, hours, minutes


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

client = redis.StrictRedis()
stats = TS(client, base_key='stats', granularities=granularities, timezone=pytz.UTC)
