import pytest

from bitcaster.utils.email_verification import (check_new_email_address_request,
                                                clear_new_email_address_request,
                                                set_request_new_email_address,)

pytestmark = pytest.mark.django_db


def test_set_new_email_request(user1):
    set_request_new_email_address(user1, 'aa')


def test_get_new_email_request(user1):
    assert not check_new_email_address_request(user1)


def test_clear_new_email_address_request(user1):
    clear_new_email_address_request(user1)
