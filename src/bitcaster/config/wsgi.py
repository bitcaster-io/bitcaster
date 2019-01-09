import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcaster.config.settings')
application = WhiteNoise(get_wsgi_application())
application.add_files(settings.STATIC_ROOT)
