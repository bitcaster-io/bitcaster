from unittest.mock import Mock

from bitcaster.web.templatetags.gravatar import gravatar


def test_gravatar():
    assert gravatar(Mock(email='s.apostolico@gmail.scom'))
