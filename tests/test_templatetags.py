# -*- coding: utf-8 -*-
from bitcaster.templatetags.bitcaster import httpiefy, jsonify


def test_httpiefy():
    assert httpiefy({'a': 1, 'b': '33'}) == 'a=1 b=33'
    assert httpiefy({}) == ''


def test_jsonify():
    assert jsonify({'a': 1, 'b': 22}) == '{"a": 1, "b": 22}'
