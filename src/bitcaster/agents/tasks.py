from bitcaster.models import Monitor


def check_all():
    for monitor in Monitor.objects.all():
        monitor.handler.poll()
    return True


def check(id):
    pass
