from bitcaster.utils.language import flatten, get_attr, repr_list


def test_flatten():
    assert flatten([1, 2, [3, 4], (5, 6)]) == [1, 2, 3, 4, 5, 6]
    assert flatten([[[1, 2, 3], (42, None)], [4, 5], [6], 7, (8, 9, 10)]) == [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]


def test_get_attr():
    class C:
        pass

    a = C()
    a.b = C()
    a.b.c = 4
    assert get_attr(a, 'b.c') == 4

    assert get_attr(a, 'b.c.y', None) is None
    assert get_attr(a, 'b.c.y', 1) == 1


def test_repr_list():
    assert repr_list([1, 2, 3]) == "'1', '2', '3'"
