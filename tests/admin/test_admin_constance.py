# mypy: disable-error-code="union-attr"
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.test.client import RequestFactory
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from bitcaster.admin.constance import CustomConstanceForm
from bitcaster.state import state

if TYPE_CHECKING:
    from django.http import HttpRequest

    from bitcaster.models import Channel, Group


@pytest.fixture
def app(django_app_factory: MixinWithInstanceVariables, rf: RequestFactory) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request: HttpRequest = rf.get("/")
    request.user = admin_user

    with state.configure(request=request):
        yield django_app


def test_save_constance(app: DjangoTestApp, group: "Group", email_channel: "Channel") -> None:
    url = reverse("admin:constance_config_changelist")
    res = app.get(url)
    res = res.forms["changelist-form"].submit()
    assert res.status_code == 302


@patch("constance.forms.ConstanceForm.__init__", return_value=None)
@patch("bitcaster.forms.unfold.UnfoldForm.__init__", return_value=None)
def test_custom_constance_form_clean_valid(mock_unfold_init, mock_constance_init):
    form = CustomConstanceForm()
    form.cleaned_data = {
        "OCCURRENCE_DEFAULT_RETENTION": 30,
        "OCCURRENCE_MAX_RETENTION": 60,
    }
    # Should not raise
    form.clean()


@patch("constance.forms.ConstanceForm.__init__", return_value=None)
@patch("bitcaster.forms.unfold.UnfoldForm.__init__", return_value=None)
def test_custom_constance_form_clean_invalid(mock_unfold_init, mock_constance_init):
    form = CustomConstanceForm()
    form.cleaned_data = {
        "OCCURRENCE_DEFAULT_RETENTION": 100,
        "OCCURRENCE_MAX_RETENTION": 60,
    }
    with pytest.raises(ValidationError, match="Default retention cannot be greater than maximum retention."):
        form.clean()


@patch("constance.forms.ConstanceForm.__init__", return_value=None)
@patch("bitcaster.forms.unfold.UnfoldForm.__init__", return_value=None)
def test_custom_constance_form_clean_defaults(mock_unfold_init, mock_constance_init):
    form = CustomConstanceForm()
    form.cleaned_data = {}
    # Should use defaults from constants and not raise
    form.clean()
