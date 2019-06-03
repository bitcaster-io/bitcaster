from logging import getLogger

from constance import config
from django.core.mail import EmailMultiAlternatives, get_connection

from bitcaster.celery import app

logger = getLogger(__name__)


@app.task()
def send_mail_async(subject, message, html_message, recipient_list,
                    *,
                    from_email=None,
                    fail_silently=False):
    try:
        connection = get_connection(
            fail_silently=fail_silently,
            username=config.EMAIL_HOST_USER,
            password=config.EMAIL_HOST_PASSWORD,
            use_tls=config.EMAIL_USE_TLS,
            host=config.EMAIL_HOST,
            port=config.EMAIL_HOST_PORT,
            timeout=config.EMAIL_TIMEOUT
        )
        mail = EmailMultiAlternatives(subject, message,
                                      from_email,
                                      recipient_list,
                                      connection=connection)
        if html_message:
            mail.attach_alternative(html_message, 'text/html')
        sent = mail.send()
        if sent != 1:
            raise Exception('Problem sending email')
        logger.debug(f"Email '{subject}' sent to {recipient_list}")
        return sent
    except Exception as e:
        logger.exception(e)
        raise
