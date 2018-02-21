import os


def pytest_configure(config):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    import django
    django.setup()
