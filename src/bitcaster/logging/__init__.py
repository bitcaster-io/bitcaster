# from bitcaster.models.subscription import Subscription
# from bitcaster.models.error import ErrorEntry
# from bitcaster.models.subscription import Subscription
# from constance import config

# from bitcaster.models.counters import Counter
# from bitcaster.models.error import ErrorEvent
# from bitcaster.models.notification import Notification
# from bitcaster.models.occurence import Occurence
# def log_notification(subscription, **kwargs):
#     pass
#     return Notification.log(subscription, **kwargs)
# from bitcaster.tsdb.db import stats

# from bitcaster.tsdb.db import counters
#

# def occurence_update_queue(value):
#     if value == '+':
#         pass
#
#
# def dequeue_occurence():
#     pass

#     # pass
#     Counter.objects.increment(event)
#     return Occurence.log(event)
#
#
# def register_error(section, pk, error_type, target, application, **kwargs):
#     pass
#     # ErrorEntry.objects.create(event=error_type,
#     #                           application=application,
#     #                           target=target,
#     #                           data=kwargs)
#     # key = '%s:%s:errors' % (section, pk)
#     # counters.increase(key)
#     # return counters.get_buckets(key, 'd', 1)[0][1]
#
#
# def register_error_subscription(pk, **kwargs):
#     pass
#     # target = Subscription.objects.get(pk=pk)
#     # return register_error('subscription', pk,
#     #                       error_type=ErrorEvent.SUBSCRIPTION_ERROR,
#     #                       target=target,
#     #                       application=target.application,
#     #                       **kwargs)
