# -*- coding: utf-8 -*-
"""
mercury / mail
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from constance import config
from django.utils.translation import gettext as _
from django.core.mail import send_mail as _send_mail, get_connection

logger = logging.getLogger(__name__)


def send_mail(subject, message, html_message, from_email,
              recipient_list, fail_silently=False):
    connection = get_connection(
        fail_silently=fail_silently,

        username=config.EMAIL_HOST_USER,
        password=config.EMAIL_HOST_PASSWORD,
        use_tls=config.EMAIL_USE_TLS,
        host=config.EMAIL_HOST,
        port=config.EMAIL_HOST_PORT,
        timeout=config.EMAIL_TIMEOUT
    )

    return _send_mail(subject=subject,
                      message=message,
                      html_message=html_message,
                      from_email='bitcaster@os4d.org',
                      recipient_list=recipient_list,
                      connection=connection)
