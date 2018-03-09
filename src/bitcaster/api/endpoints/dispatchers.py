# -*- coding: utf-8 -*-
from rest_framework import viewsets
from rest_framework.response import Response

from bitcaster import logging
from bitcaster.utils import fqn

logger = logging.getLogger(__name__)


class DispatcherViewSet(viewsets.ViewSet):
    def list(self, request):
        from bitcaster.dispatchers.registry import dispatcher_registry
        ret = []
        for entry in dispatcher_registry:
            ret.append({"fqn": fqn(entry),
                        "name": entry.name,
                        "author": entry.author,
                        "license": entry.license,
                        })
        # values = sorted([fqn(klass) for klass in dispatcher_registry])

        # return Response(dict(dispatcher_registry.as_choices()))
        return Response(ret)
