from bitcaster.models import Monitor


def check_all():
    for monitor in Monitor.objects.all():
        monitor.poll()


def check(id):
    pass
