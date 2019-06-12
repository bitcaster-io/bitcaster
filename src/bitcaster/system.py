from django.utils.functional import SimpleLazyObject


class System:
    def __init__(self):
        from django.core.cache import caches
        self.storage = caches['lock']

    def stop(self):
        self.storage.set('STOP', 1)

    def running(self):
        return self.storage.get('STOP', 0) == '1'

    def stopped(self):
        return not self.running()

    def restart(self):
        self.storage.delete('STOP')


sys = SimpleLazyObject(System)

stop = sys.stop
stopped = sys.stopped
running = sys.running
restart = sys.restart
