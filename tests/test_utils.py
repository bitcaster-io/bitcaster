# -*- coding: utf-8 -*-
import pytest

from mercury.utils.language import flatten, get_attr

values = ([1, 2, 3, 4, 5],
          [1, (2, 3), 4, 5],
          [1, (2, 3), (4, 5)],
          [(1, (2, 3), (4, 5))],
          )


@pytest.mark.parametrize("param", values, ids=list(map(str, values)))
def test_flatten(param):
    assert flatten(param) == [1, 2, 3, 4, 5]


def test_get_attr():
    class C(object):
        pass

    a = C()
    a.b = C()
    a.b.c = 4
    assert get_attr(a, 'b.c') == 4
    assert get_attr(a, 'b.c.y', None) is None
