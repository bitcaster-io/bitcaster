from collections import OrderedDict

from django.utils.functional import cached_property
from rest_framework import serializers


class Configuration(serializers.Serializer):
    """
        fieldsets = {'common': ['fieldname1',...],
                     'security': ['fieldname11',...],
                    }
    """
    fieldset_defs = None

    @cached_property
    def fieldsets(self):
        ret = OrderedDict()
        if self.fieldset_defs:
            added = []
            _fields = {f.name: f for f in self}

            for group_name, fieldnames in self.fieldset_defs:
                ret[group_name] = []
                for field_name in fieldnames:
                    ret[group_name].append(_fields[field_name])
                    added.append(field_name)

            remaining = []

            for field_name, field in _fields.items():
                if field_name not in added:
                    remaining.append(_fields[field_name])
            if remaining:
                ret['Settings'] = remaining
        else:
            ret['Settings'] = [f for f in self]
        return ret
