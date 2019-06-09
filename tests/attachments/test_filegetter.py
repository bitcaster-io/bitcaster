from unittest.mock import Mock

import pytest
from PIL import Image

from bitcaster.attachments import HttpRetriever
from bitcaster.attachments.base import RetrieverOptions

pytestmark = pytest.mark.django_db


# "https://www.gravatar.com/avatar/%s?%s" % \
# (hashlib.md5(email.lower()).hexdigest(), urllib.urlencode({'d':default, 's':str(size)}))

@pytest.mark.plugin
def test_filegetter():
    subscriber = Mock(email='guido@python.org')
    subscription = Mock(subscriber=subscriber)
    config = {'default': 'https://example.com/static/images/defaultavatar.jpg',
              'parser': RetrieverOptions.PARSER_JINJA,
              'url_pattern': 'https://www.gravatar.com/avatar/{{subscription.subscriber.email|lower|md5|hexdigest}}',
              'name_pattern': '{{subscription.subscriber.email|lower|slugify}}.png'
              }

    r = HttpRetriever(Mock(config=config))
    response = r.get(subscription)
    Image.open(response.content)
    assert response.name == 'guido-python-org.png'
