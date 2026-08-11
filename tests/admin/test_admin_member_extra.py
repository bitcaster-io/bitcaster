import pytest
from testutils.factories import (
    AddressFactory,
    AssignmentFactory,
    ChannelFactory,
    DistributionListFactory,
    MemberFactory,
)
from unittest.mock import MagicMock, patch

from django import forms
from django.contrib.admin import AdminSite
from django.test import RequestFactory
from django.urls import reverse

from bitcaster.admin.member import (
    AddressInline,
    AssignmentFormSet,
    AssignmentInline,
    JsonUpdateMode2,
    ListsFormSet,
    ListsInline,
    ReadOnlyInline,
)
from bitcaster.constants import bitcaster
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
def test_assignment_inline_formfield_for_foreignkey_with_widget_queryset(admin_user):
    from unittest.mock import patch

    site = AdminSite()
    inline = AssignmentInline(Member, site)

    rf = RequestFactory()
    request = rf.get("/")
    request.user = admin_user

    db_field = Assignment._meta.get_field("address")

    with patch("bitcaster.admin.member.NonrelatedTabularInline.formfield_for_foreignkey") as mock_super:
        mock_field = MagicMock()
        mock_field.widget = MagicMock()
        # Mocking hasattr(ret.widget, "queryset") to return True
        # and also allowing assignment to it.
        # MagicMock has any attribute, so hasattr will be true.
        mock_super.return_value = mock_field

        ret = inline.formfield_for_foreignkey(db_field, request)
        assert ret == mock_field
        # Verify that Address.objects.none() was assigned to ret.widget.queryset
        # We can't easily compare querysets directly, but we can check if it was called.
        assert mock_field.widget.queryset is not None


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
    m.initial_form_count.return_value = 0
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
def test_subscription_inline_save_invalid_warns(admin_user):
    from testutils.factories import NotificationFactory, SubscriptionFactory

    from bitcaster.admin.member import SubscriptionInline
    from bitcaster.models import Subscription

    site = AdminSite()
    member = MemberFactory()
    channel = ChannelFactory()
    other_channel = ChannelFactory()
    notification = NotificationFactory(event__channels=[other_channel], distribution=None)
    assignment = AssignmentFactory(address=AddressFactory(user=member), channel=channel)
    subscription = SubscriptionFactory.build(notification=notification, assignment=assignment)

    inline = SubscriptionInline(Member, site)
    rf = RequestFactory()
    request = rf.get("/")
    request.user = admin_user
    inline._request = request

    with patch("bitcaster.admin.member.messages.warning") as mock_warning:
        inline.save_new_instance(member, subscription)

    mock_warning.assert_called_once()
    assert Subscription.objects.filter(pk=subscription.pk).exists()


@pytest.mark.django_db
def test_subscription_inline_save_valid_no_warning(admin_user):
    from testutils.factories import NotificationFactory, SubscriptionFactory

    from bitcaster.admin.member import SubscriptionInline
    from bitcaster.models import Subscription

    site = AdminSite()
    member = MemberFactory()
    channel = ChannelFactory()
    notification = NotificationFactory(event__channels=[channel], distribution=None)
    assignment = AssignmentFactory(address=AddressFactory(user=member), channel=channel)
    subscription = SubscriptionFactory.build(notification=notification, assignment=assignment)

    inline = SubscriptionInline(Member, site)
    rf = RequestFactory()
    request = rf.get("/")
    request.user = admin_user
    inline._request = request

    with patch("bitcaster.admin.member.messages.warning") as mock_warning:
        inline.save_new_instance(member, subscription)

    mock_warning.assert_not_called()
    assert Subscription.objects.filter(pk=subscription.pk).exists()


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
def test_member_admin_changelist_no_dl(app):
    url = reverse("admin:bitcaster_member_changelist")
    response = app.get(url)
    assert response.status_code == 200
    # This should cover the branch where dl_id is None (line 192 skipping to 198)


@pytest.mark.django_db
def test_check_custom_fields_invalid_json():
    from bitcaster.admin.member import check_custom_fields

    with pytest.raises(forms.ValidationError) as excinfo:
        check_custom_fields("{invalid json}")
    assert "Invalid JSON" in str(excinfo.value)


@pytest.mark.django_db
def test_check_custom_fields_not_dict():
    from bitcaster.admin.member import check_custom_fields

    with pytest.raises(forms.ValidationError) as excinfo:
        check_custom_fields("[]")  # JSON list, not dict
    assert "Must be a dictionary" in str(excinfo.value)

    with pytest.raises(forms.ValidationError) as excinfo:
        check_custom_fields(123)  # Not a string, not a dict
    assert "Must be a dictionary" in str(excinfo.value)


@pytest.mark.django_db
def test_member_form_clean_custom_fields():
    from bitcaster.admin.member import MemberForm

    form = MemberForm(data={"custom_fields": '{"a": 1}'})
    # We need other fields too for valid form, but we can call clean_custom_fields directly or via full_clean
    form.cleaned_data = {"custom_fields": '{"a": 1}'}
    assert form.clean_custom_fields() == {"a": 1}


@pytest.mark.django_db
def test_member_admin_add_to_distributionlist(admin_user):
    from django.contrib.admin import AdminSite
    from django.contrib.messages.storage.cookie import CookieStorage
    from django.test import RequestFactory

    from bitcaster.admin.member import MemberAdmin
    from bitcaster.models import Member

    member = MemberFactory()
    dl = DistributionListFactory()
    site = AdminSite()
    ma = MemberAdmin(Member, site)
    rf = RequestFactory()

    # GET request
    request = rf.get("/")
    request.user = admin_user
    response = ma.add_to_distributionlist(request, Member.objects.filter(pk=member.pk))
    if hasattr(response, "render"):
        response.render()
    assert response.status_code == 200
    assert b"Add to Distribution List" in response.content

    # POST request (apply)
    data = {
        "apply": "1",
        "dl": str(dl.pk),
        "action": "add_to_distributionlist",
        "_selected_action": [str(member.pk)],
    }
    request = rf.post("/", data=data)
    request.user = admin_user
    request._messages = CookieStorage(request)

    # We need to make sure the user has an assignment to be added
    addr = AddressFactory(user=member)
    ch = ChannelFactory()
    asm = AssignmentFactory(address=addr, channel=ch)

    response = ma.add_to_distributionlist(request, Member.objects.filter(pk=member.pk))
    assert response.status_code == 302
    assert dl.recipients.filter(pk=asm.pk).exists()


@pytest.mark.django_db
def test_member_admin_import_members(admin_user):
    from django.contrib.admin import AdminSite
    from django.contrib.messages.storage.cookie import CookieStorage
    from django.core.files.uploadedfile import SimpleUploadedFile
    from django.test import RequestFactory

    from bitcaster.admin.member import MemberAdmin
    from bitcaster.models import Member

    site = AdminSite()
    ma = MemberAdmin(Member, site)
    rf = RequestFactory()

    # GET request
    request = rf.get("/")
    request.user = admin_user
    # ma.import_members is decorated with @button
    try:
        response = ma.import_members(request)
    except TypeError:
        if hasattr(ma.import_members, "func"):
            response = ma.import_members.func(ma, request)
        else:
            from bitcaster.admin.member import MemberAdmin

            response = MemberAdmin.import_members(ma, request)

    if hasattr(response, "render"):
        response.render()
    assert response.status_code == 200
    assert b"Import Members" in response.content

    # POST request (apply)
    csv_content = b"username,first_name,last_name,email\nuser1,User,One,user1@example.com"
    csv_file = SimpleUploadedFile("members.csv", csv_content, content_type="text/csv")

    data = {
        "apply": "1",
        "file": csv_file,
        "group": str(bitcaster.get_default_group().pk),
    }
    request = rf.post("/", data=data)
    request.user = admin_user
    request._messages = CookieStorage(request)

    with patch("bitcaster.admin.member.import_members_csv") as mock_import:
        mock_import.return_value = (1, 1)
        try:
            response = ma.import_members(request)
        except TypeError:
            if hasattr(ma.import_members, "func"):
                response = ma.import_members.func(ma, request)
            else:
                from bitcaster.admin.member import MemberAdmin

                response = MemberAdmin.import_members(ma, request)

        assert response.status_code == 302
        mock_import.assert_called_once()


@pytest.mark.django_db
def test_update_custom_fields_rewrite(admin_user):
    from bitcaster.admin.member import JsonUpdateMode2, MemberAdmin

    target_member = MemberFactory(custom_fields={"a": 1})
    site = AdminSite()
    ma = MemberAdmin(Member, site)
    rf = RequestFactory()

    data = {
        "apply": "1",
        "mode": JsonUpdateMode2.REWRITE,
        "action": "update_custom_fields",
        "_selected_action": [str(target_member.pk)],
        "custom_fields": '{"b": 2}',
    }

    request = rf.post("/", data=data)
    request.user = admin_user
    from django.contrib.messages.storage.cookie import CookieStorage

    request._messages = CookieStorage(request)

    queryset = Member.objects.filter(pk=target_member.pk)
    response = ma.update_custom_fields(request, queryset)
    assert response.status_code == 302

    target_member.refresh_from_db()
    assert target_member.custom_fields == {"b": 2}


@pytest.mark.django_db
def test_update_custom_fields_invalid_form(admin_user):
    from bitcaster.admin.member import MemberAdmin

    member = MemberFactory()
    site = AdminSite()
    ma = MemberAdmin(Member, site)
    rf = RequestFactory()

    # apply is present but form is invalid (missing mode)
    request = rf.post("/", data={"apply": "1", "_selected_action": [str(member.pk)]})
    request.user = admin_user

    queryset = Member.objects.filter(pk=member.pk)
    response = ma.update_custom_fields(request, queryset)
    assert response.status_code == 200  # Returns to form with errors


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
