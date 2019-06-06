from io import BytesIO

import pytest

from bitcaster.attachments.base import Attachment
from bitcaster.models import Notification

pytestmark = pytest.mark.django_db


# "https://www.gravatar.com/avatar/%s?%s" % \
# (hashlib.md5(email.lower()).hexdigest(), urllib.urlencode({'d':default, 's':str(size)}))

def test_store():
    a = Attachment('name.txt', BytesIO(b'aaa'), 'text/plain')
    n = Notification(attachments=[a])
    n.save()
    n.refresh_from_db()

    assert n.attachments[0].name == 'name.txt'
    assert n.attachments[0].content.read() == b'aaa'
    assert n.attachments[0].content_type == 'text/plain'
