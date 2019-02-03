# -*- coding: utf-8 -*-
import ipaddress


class NetList:
    def __init__(self, *nets) -> None:
        args = self._coerce(*nets)
        self._list = args

    def _coerce(self, *args):
        ret = []
        for value in args:
            value = ipaddress.ip_network(value)
            ret.append(value)
        return ret

    def __setitem__(self, key, value):
        self._list[key] = ipaddress.ip_network(value)

    def __getitem__(self, key):
        return self._list[key]

    def __iter__(self):
        return iter(self._list)

    def __contains__(self, item):
        item = ipaddress.ip_address(item)
        for e in self._list:
            if item in e:
                return True
        return False
