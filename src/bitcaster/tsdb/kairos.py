# from collections import OrderedDict
#
# import pytz
# from django.conf import settings
# from django.utils.functional import SimpleLazyObject
# from redis import StrictRedis
# from redis_timeseries import (TimeSeries, days, hours, minutes,
#                               round_time_with_tz, seconds,)
#
# # class TS(TimeSeries):
# #
# #     def increase(self, key, amount=1, timestamp=None, execute=True):
# #         super().increase(key, amount, timestamp, execute)
# #
# #     def decrease(self, key, amount=1, timestamp=None, execute=True):
# #         super().decrease(key, amount, timestamp, execute)
# #
# #     def get_data(self, key, granularity='h', count=None):
# #         if count is None:
# #             props = self.granularities[granularity]
# #             count = props['ttl'] // props['duration']
# #
# #         return self.get_buckets(key, granularity, count)
# #
# #
# #     def add(self, key, amount, timestamp=None, execute=True):
# #         pipe = self.client.pipeline() if execute else self.chain
# #
# #         for granularity, props in self.granularities.items():
# #             hkey = self.get_key(key, timestamp, granularity)
# #             bucket = round_time_with_tz(timestamp, props['duration'], self.timezone)
# #
# #             pipe.hset(hkey, bucket, amount)
# #
# #             pipe.expire(hkey, props['ttl'])
# #
# #         if execute:
# #             pipe.execute()
# #
# #     def set(self, key, amount, timestamp=None, execute=True):
# #         pipe = self.client.pipeline() if execute else self.chain
# #
# #         for granularity, props in self.granularities.items():
# #             hkey = self.get_key(key, timestamp, granularity)
# #             bucket = round_time_with_tz(timestamp, props['duration'], self.timezone)
# #
# #             pipe.hset(hkey, bucket, amount)
# #
# #             pipe.expire(hkey, props['ttl'])
# #
# #         if execute:
# #             pipe.execute()
#
#
# # def get_timeseries(*args, **kwargs):
# #     client = StrictRedis.from_url(settings.TSDB_STORE)
# #     return TS(client,
# #               base_key='stats',
# #               timezone=pytz.UTC)
#
# # sss = TimeSeries(StrictRedis.from_url(settings.TSDB_STORE))
