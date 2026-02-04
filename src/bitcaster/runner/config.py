import dramatiq

__all__ = ["dramatiq", "SCHEDULER"]

SECOND = 1000
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24

SCHEDULER = {
    "scan_occurrences": {
        "func": "bitcaster.runner.tasks.scan_occurrences",
        "replace_existing": True,
        "trigger": "interval",
        "minutes": 1,
    },
    "purge_occurrences": {
        "func": "bitcaster.runner.tasks.purge_occurrences",
        "replace_existing": True,
        "trigger": "interval",
        "days": 30,
    },
    "monitor_run": {
        "func": "bitcaster.runner.tasks.monitor_run",
        "replace_existing": True,
        "trigger": "interval",
        "minutes": 5,
    },
    "check_for_new_user_messages": {
        "func": "bitcaster.runner.tasks.check_for_new_user_messages",
        "replace_existing": True,
        "trigger": "interval",
        "minutes": 5,
    },
    "delete_expired_user_messages": {
        "func": "bitcaster.runner.tasks.delete_expired_user_messages",
        "replace_existing": True,
        "trigger": "interval",
        "days": 1,
    },
}
