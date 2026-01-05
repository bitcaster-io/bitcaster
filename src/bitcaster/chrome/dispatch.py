import base64
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def send_message(email: str, event: str, **data):
    """Send a message to a user's Chrome extension via WebSockets."""
    try:
        channel_layer = get_channel_layer()
        # Encode the email to create a safe group name
        safe_email = base64.urlsafe_b64encode(email.encode()).decode()
        group_name = f"chrome_{safe_email}"

        logger.debug(f"Sending event '{event}' to group '{group_name}' for user '{email}'")

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chrome.message",
                "event": event,
                "data": data,
            },
        )
        return True
    except Exception as e:
        logger.exception(f"Error sending WebSocket message to {email}: {e}")
        return False
