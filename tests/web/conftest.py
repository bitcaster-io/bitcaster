import pytest
from bitcaster.state import state
from django.http import HttpRequest


@pytest.fixture()
def app(django_app_factory, rf, admin_user, settings):
    settings.FLAGS = {"BETA_PREVIEW_LOCKING": [("boolean", True)]}

    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request: HttpRequest = rf.get("/")
    request.user = admin_user
    with state.configure(request=request):
        yield django_app
