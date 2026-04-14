from unittest.mock import MagicMock

import pytest
from django.contrib.admin import AdminSite
from django.test import RequestFactory
from django.urls import reverse
from testutils.factories import (
    AddressFactory,
    AssignmentFactory,
    ChannelFactory,
    DistributionListFactory,
    MemberFactory,
)

from bitcaster.admin.member import (
    AddressInline,
    AssignmentFormSet,
    AssignmentInline,
    JsonUpdateMode2,
    ListsFormSet,
    ListsInline,
    ReadOnlyInline,
)
from bitcaster.models import Address, Assignment, Member


@pytest.fixture
def app(django_app_factory, admin_user):
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.mark.django_db
def test_member_admin_inlines(app):
    member = MemberFactory()
    AddressFactory(user=member)
    ch = ChannelFactory()
    AssignmentFactory(address__user=member, channel=ch)

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    response = app.get(url)
    assert response.status_code == 200
    # Check if inlines are present in the response
    assert b"Addresses" in response.content
    assert b"Assignments" in response.content
    assert b"Distribution Lists" in response.content


@pytest.mark.django_db
def test_member_admin_readonly_fields(app):
    member = MemberFactory()
    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    response = app.get(url)

    # These fields should be readonly in the change form
    assert b"readonly" in response.content
    assert member.username.encode() in response.content
    assert member.email.encode() in response.content


@pytest.mark.django_db
def test_member_admin_changelist_subtitle(app):
    dl = DistributionListFactory(name="Test List")
    url = reverse("admin:bitcaster_member_changelist")
    response = app.get(f"{url}?dl={dl.pk}")
    assert response.status_code == 200
    assert b"Members selected for distribution list: Test List" in response.content


@pytest.mark.parametrize("mode", [JsonUpdateMode2.REMOVE, JsonUpdateMode2.OVERRIDE])
@pytest.mark.django_db
def test_update_custom_fields_all_modes(admin_user, mode):
    from bitcaster.admin.member import MemberAdmin

    target_member = MemberFactory(custom_fields={"a": 1, "b": 2})

    site = AdminSite()
    ma = MemberAdmin(Member, site)
    rf = RequestFactory()

    common_data = {
        "apply": "1",
        "mode": mode,
        "action": "update_custom_fields",
        "_selected_action": [str(target_member.pk)],
        "select_across": "0",
    }
    if mode == JsonUpdateMode2.REMOVE:
        data = {**common_data, "custom_fields": '{"a": 1}'}
    else:
        data = {**common_data, "custom_fields": '{"c": 3}'}

    request = rf.post("/", data=data)
    request.user = admin_user
    from django.contrib.messages.storage.cookie import CookieStorage

    request._messages = CookieStorage(request)

    queryset = Member.objects.filter(pk=target_member.pk)

    response = ma.update_custom_fields(request, queryset)
    assert response.status_code == 302

    target_member.refresh_from_db()
    if mode == JsonUpdateMode2.REMOVE:
        assert "a" not in target_member.custom_fields
        assert "b" in target_member.custom_fields
    else:
        assert target_member.custom_fields == {"c": 3}


@pytest.mark.django_db
def test_assignment_inline_formfield_for_foreignkey(admin_user):
    site = AdminSite()
    inline = AssignmentInline(Member, site)

    rf = RequestFactory()
    request = rf.get("/")
    request.user = admin_user

    # Test that address queryset is empty as intended in the inline
    db_field = Assignment._meta.get_field("address")
    formfield = inline.formfield_for_foreignkey(db_field, request)
    assert formfield.queryset.count() == 0


@pytest.mark.django_db
def test_member_admin_formsets(admin_user):
    member = MemberFactory()

    # Test AssignmentFormSet.get_form_kwargs logic
    m = MagicMock(spec=AssignmentFormSet)
    m.instance = member
    m.form_kwargs = {}
    # Call the actual method
    ret = AssignmentFormSet.get_form_kwargs(m, 0)
    assert ret["user"] == member

    # Test ListsFormSet.get_form_kwargs logic
    m = MagicMock(spec=ListsFormSet)
    m.instance = member
    m.form_kwargs = {}
    ret = ListsFormSet.get_form_kwargs(m, 0)
    assert ret["user"] == member


@pytest.mark.django_db
def test_inline_permissions_and_save(admin_user):
    site = AdminSite()
    member = MemberFactory()
    new_member = MemberFactory.build()  # no PK

    rf = RequestFactory()
    request = rf.get("/")
    request.user = admin_user

    # AddressInline
    inline = AddressInline(Member, site)
    assert bool(inline.has_add_permission(request, member)) is True
    assert bool(inline.has_add_permission(request, new_member)) is False
    assert list(inline.get_form_queryset(member)) == list(Address.objects.filter(user=member))

    # AssignmentInline
    inline = AssignmentInline(Member, site)
    assert bool(inline.has_add_permission(request, member)) is True
    assert bool(inline.has_add_permission(request, new_member)) is False
    assert list(inline.get_form_queryset(member)) == list(Assignment.objects.filter(address__user=member))

    # We must have address and channel saved
    addr = AddressFactory(user=member)
    ch = ChannelFactory.create()
    ass = AssignmentFactory.build(address=addr, channel=ch)
    inline.save_new_instance(member, ass)
    assert ass.pk is not None

    # ListsInline
    inline = ListsInline(Member, site)
    assert list(inline.get_form_queryset(member)) == list(member.get_distribution_lists())
    dl = DistributionListFactory.create()
    inline.save_new_instance(member, dl)
    assert dl.pk is not None


@pytest.mark.django_db
def test_member_admin_changelist_invalid_dl(app):
    url = reverse("admin:bitcaster_member_changelist")
    # dl=invalid (not an int or not exists)
    response = app.get(f"{url}?dl=999999")
    assert response.status_code == 200
    assert b"Members selected for distribution list:" not in response.content


@pytest.mark.django_db
def test_update_custom_fields_get(admin_user):
    from bitcaster.admin.member import MemberAdmin

    member = MemberFactory()
    site = AdminSite()
    ma = MemberAdmin(Member, site)
    rf = RequestFactory()

    # Test GET request to update_custom_fields
    request = rf.post("/", data={"action": "update_custom_fields", "_selected_action": [str(member.pk)]})
    request.user = admin_user
    # No "apply" in POST, should return the form
    queryset = Member.objects.filter(pk=member.pk)
    response = ma.update_custom_fields(request, queryset)
    assert response.status_code == 200
    assert b"Update Custom Fields" in response.content


@pytest.mark.django_db
def test_readonly_inline_defaults():
    roi = ReadOnlyInline()
    assert roi.extra == 0
    assert roi.tab is True
    assert roi.has_delete_permission(None, None) is False
    assert roi.has_add_permission(None, None) is False
    assert roi.has_change_permission(None, None) is False
    # save_new_instance should do nothing
    roi.save_new_instance(None, None)
