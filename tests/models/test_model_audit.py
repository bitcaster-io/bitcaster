import pytest

from bitcaster.models import AuditEvent, AuditLogEntry


@pytest.mark.django_db
def test_create_actor(organization1, user1):
    c = AuditLogEntry(organization=organization1,
                      event=AuditEvent.MEMBER_LOGIN,
                      actor=user1)
    c.save()
    assert c.pk


@pytest.mark.django_db
def test_create_actor_label(organization1, user1):
    c = AuditLogEntry(organization=organization1,
                      event=AuditEvent.MEMBER_LOGIN,
                      actor_label='label_1',
                      actor=user1)
    c.save()
    assert c.pk

#
# @pytest.mark.django_db
# def test_create_application(organization1):
#     c = AuditLogEntry(organization=organization1,
#                       event=AuditEvent.MEMBER_LOGIN, application=application1)
#     c.clean()
#     c.save()
#     assert c.pk
#
#
# @pytest.mark.django_db
# def test_create_target(event1):
#     c = AuditLogEntry(event=AuditEvent.MEMBER_LOGIN, target=event1)
#     c.clean()
#     c.save()
#     assert c.pk
#
#
# @pytest.mark.django_db
# def test_create_fail(subscription1):
#     c = AuditLogEntry(event=AuditEvent.MEMBER_LOGIN, target=subscription1)
#     with pytest.raises(ObjectDoesNotExist):
#         c.save()
