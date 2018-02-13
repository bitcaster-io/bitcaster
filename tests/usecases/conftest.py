from unittest.mock import Mock

import pytest


@pytest.fixture(autouse=True)
def disable_create_extra_permission(monkeypatch):
    monkeypatch.setattr('mercury.apps.create_extra_permission', Mock())
    monkeypatch.setattr('mercury.apps.post_migrate', Mock())
