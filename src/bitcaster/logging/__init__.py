from constance import config

# from bitcaster.models.subscription import Subscription
from bitcaster.models.counters import Counter
from bitcaster.models.notification import Notification
from bitcaster.models.occurence import Occurence


def log_notification(subscription, **kwargs) -> Notification:
    return Notification.log(subscription, **kwargs)


def log_occurence(event, **kwargs):
    """

    :param bitcaster.models.Event event:
    :param kwargs:
    :return:
    """
    Counter.objects.increment(event)
    if config.LOG_OCCURENCES:
        return Occurence.log(event, **kwargs)
