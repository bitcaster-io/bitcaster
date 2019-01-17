from django.conf import settings

if hasattr(settings, 'RAVEN_CONFIG'):
    from raven import Client

    client = Client(settings.RAVEN_CONFIG['dsn'])
else:
    class NoopSentryClient:
        def captureException(self, *args, **kwargs):
            pass

        def get_ident(self, *args, **kwargs):
            pass

    client = NoopSentryClient()
