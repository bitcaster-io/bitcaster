# -*- coding: utf-8 -*-
"""
mercury / mail
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from constance import config
from django.core.mail import get_connection, send_mail as _send_mail
from django.template.loader import get_template

from mercury.tasks import send_mail_async
from mercury.template.secure_context import SecureContext

logger = logging.getLogger(__name__)


def make_message(template_name, context):
    _html = f"bitcaster/emails/{template_name}.html"
    _text = f"bitcaster/emails/{template_name}.txt"
    return (get_template(_html).render(context),
            get_template(_text).render(context))


def send_mail_by_template(subject, template_name, context,
                          recipient_list, *,
                          from_email=None,
                          async=True,
                          fail_silently=False):
    html_message, message = make_message(template_name, context)

    if async:
        return send_mail_async(subject, message, html_message,
                               recipient_list,
                               from_email=from_email,
                               fail_silently=fail_silently)
    else:
        return send_mail(subject, message, html_message,
                         recipient_list,
                         from_email=from_email,
                         fail_silently=fail_silently)


def send_mail(subject, message, html_message,
              recipient_list, *, from_email=None, fail_silently=False):
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
                      from_email=from_email,
                      recipient_list=recipient_list,
                      connection=connection)
