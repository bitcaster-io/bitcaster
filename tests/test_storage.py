# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest

from bitcaster.file_storage import (app_media_root, org_media_root,
                                    profile_media_root,)


@pytest.fixture
def tmpdir(tmpdir):
    assert tmpdir.isdir()
    yield Path(str(tmpdir))
    tmpdir.remove(ignore_errors=True)


def test__get_media_root():
    assert profile_media_root(Mock(), 'aaa')
    assert org_media_root(Mock(), 'aaa')
    assert app_media_root(Mock(), 'aaa')
