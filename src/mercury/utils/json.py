# -*- coding: utf-8 -*-
import json

from _datetime import datetime


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                '__type__': 'datetime',
                'year': obj.year,
                'month': obj.month,
                'day': obj.day,
                'hour': obj.hour,
                'minute': obj.minute,
                'second': obj.second,
                'microsecond': obj.microsecond,
            }
        return json.JSONEncoder.default(self, obj)


class Decoder(json.JSONDecoder):

    def __init__(self, *, parse_float=None,
                 parse_int=None, parse_constant=None, strict=True,
                 object_pairs_hook=None):
        super().__init__(object_hook=self.dict_to_object, parse_float=parse_float,
                         parse_int=parse_int, parse_constant=parse_constant,
                         strict=strict, object_pairs_hook=object_pairs_hook)

    def dict_to_object(self, d):
        if '__type__' not in d:
            return d

        type = d.pop('__type__')
        try:
            dateobj = datetime(**d)
            return dateobj
        except Exception:
            d['__type__'] = type
            return d
