if __name__ == '__main__':
    import os
    from django.core.wsgi import get_wsgi_application

    os.environ['DJANGO_SETTINGS_MODULE'] = 'bitcaster.config.settings'
    application = get_wsgi_application()

    from bitcaster.models import User

    User.objects.filter(email__endswith='@example.com').delete()
