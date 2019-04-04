import logging

logger = logging.getLogger(__name__)


def get_status(value=None, ok_limit=0, warn_limit=1, error_limit=10):
    if callable(value):
        value = value()
    if value == ok_limit:
        return 'success'
    elif value >= error_limit:
        return 'danger'
    elif value >= warn_limit:
        return 'warning'
    else:
        return ''


def check_enabled_disabled(org_data, entry):
    if org_data[f'enabled_{entry}'] == 0:
        v = 11
    elif org_data[f'disabled_{entry}'] > 0:
        v = 2
    else:
        v = 0
    return get_status(v)


def check_channels(org_data):
    return check_enabled_disabled(org_data, 'channels')


def check_events(org_data):
    return check_enabled_disabled(org_data, 'events')


def check_keys(org_data):
    return check_enabled_disabled(org_data, 'keys')
