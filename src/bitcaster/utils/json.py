import datetime
import json
from uuid import UUID

import pytz
from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string

from bitcaster.utils.reflect import fqn


class Encoder(json.JSONEncoder):

    def encode(self, o):
        if isinstance(o, SimpleLazyObject):
            o = str(o)
        return super().encode(o)

    def default(self, obj):
        if isinstance(obj, UUID):
            return {'__type__': fqn(UUID),
                    'value': obj.hex
                    }
        elif isinstance(obj, datetime.tzinfo):
            return {'__type__': fqn(pytz.timezone),
                    'value': getattr(obj, 'zone')
                    }
        elif isinstance(obj, datetime.datetime):
            return {
                '__type__': fqn(datetime.datetime),
                'year': obj.year,
                'month': obj.month,
                'day': obj.day,
                'hour': obj.hour,
                'minute': obj.minute,
                'second': obj.second,
                'microsecond': obj.microsecond,
                'tzinfo': str(obj.tzinfo)
            }
        elif callable(obj):
            return {'__type__': 'callable',
                    'value': fqn(obj)
                    }
        elif fqn(obj) == 'django.utils.functional.__proxy__':
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class Decoder(json.JSONDecoder):

    def __init__(self, *, parse_float=None,
                 parse_int=None, parse_constant=None, strict=True,
                 object_pairs_hook=None):
        super().__init__(object_hook=self.dict_to_object, parse_float=parse_float,
                         parse_int=parse_int, parse_constant=parse_constant,
                         strict=strict, object_pairs_hook=object_pairs_hook)

    def dict_to_object(self, d):
        try:
            if '__type__' not in d:
                return d
            if d['__type__'] == 'callable':
                return import_string(d['value'])
            if d['__type__'] == fqn(datetime.datetime):
                type = d.pop('__type__')
                try:
                    if d['tzinfo'] != 'None':
                        d['tzinfo'] = pytz.timezone(d['tzinfo'])
                    else:
                        d.pop('tzinfo')

                    dateobj = datetime.datetime(**d)
                    return dateobj
                except Exception:
                    d['__type__'] = type
                    return d
            else:
                clazz = import_string(d['__type__'])
                return clazz(d['value'])
        except Exception as e:
            raise ValueError('Unable to decode %s: %s' % (repr(d), e)) from e


loads = json.loads
dumps = json.dumps
