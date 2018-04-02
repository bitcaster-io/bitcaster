# -*- coding: utf-8 -*-
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.django_db


def test_checks(monkeypatch):
    config_file = Path(__file__).parent / 'cli/sample.conf'
    monkeypatch.setitem(os.environ, 'BITCASTER_CONF', str(config_file))

    from bitcaster.checks import check
    assert check() == []
