# -*- coding: utf-8 -*-

import pytest

from bitcaster.utils.dashboard import (check_channels, check_events,
                                       check_keys, get_status,)


@pytest.mark.parametrize('value,result', [(lambda: 0, 'success'),
                                          (0, 'success'), (2, 'warning'),
                                          (-1, ''), (11, 'danger')])
def test_get_status(value, result):
    assert get_status(value) == result


@pytest.mark.parametrize('org_data,result', [({'enabled_channels': 0}, 'danger'),
                                             ({'enabled_channels': 1,
                                               'disabled_channels': 2}, 'warning'),
                                             ({'enabled_channels': 11,
                                               'disabled_channels': 1}, 'warning'),

                                             ({'enabled_channels': 1,
                                               'disabled_channels': 0}, 'success'),
                                             ])
def test_check_channels(org_data, result):
    assert check_channels(org_data) == result


@pytest.mark.parametrize('org_data,result', [({'enabled_events': 0}, 'danger'),
                                             ({'enabled_events': 1,
                                               'disabled_events': 2}, 'warning'),
                                             ({'enabled_events': 11,
                                               'disabled_events': 1}, 'warning'),

                                             ({'enabled_events': 1,
                                               'disabled_events': 0}, 'success'),
                                             ])
def test_check_events(org_data, result):
    assert check_events(org_data) == result


@pytest.mark.parametrize('org_data,result', [({'enabled_keys': 0}, 'danger'),
                                             ({'enabled_keys': 1,
                                               'disabled_keys': 2}, 'warning'),
                                             ({'enabled_keys': 11,
                                               'disabled_keys': 1}, 'warning'),

                                             ({'enabled_keys': 1,
                                               'disabled_keys': 0}, 'success'),
                                             ])
def test_check_keys(org_data, result):
    assert check_keys(org_data) == result
