
from django.utils.functional import cached_property
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.renderers import (AdminRenderer, BrowsableAPIRenderer,
                                      JSONRenderer,)

from bitcaster.models import Application

from ..permissions import CsrfExemptSessionAuthentication, TokenAuthentication


class BaseViewSet(viewsets.ViewSet):
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, AdminRenderer)
    authentication_classes = (TokenAuthentication,
                              CsrfExemptSessionAuthentication)


# def handler(exc, context):
#     """
#     Returns the response that should be used for any given exception.
#
#     By default we handle the REST framework `APIException`, and also
#     Django's built-in `Http404` and `PermissionDenied` exceptions.
#
#     Any unhandled exceptions may return `None`, which will cause a 500 error
#     to be raised.
#     """
#     if isinstance(exc, RecordModifiedError):
#         return Response({"detail": ["Record has been modified"]},
#                         status=400)
#     else:
#         return exception_handler(exc, context)


class BaseModelViewSet(viewsets.ModelViewSet):
    # remove this when write mode will be re-enabled
    http_method_names = ['get', 'post', 'options']

    # http_method_names = ['get', 'post', 'put', 'patch', 'delete',
    #                      'head', 'options', 'trace']
    authentication_classes = (TokenAuthentication,
                              BasicAuthentication,
                              CsrfExemptSessionAuthentication)
    # renderer_classes = (JSONRenderer, BrowsableAPIRenderer, AdminRenderer)
    renderer_classes = (JSONRenderer, )

    # def get_exception_handler(self):
    #     return handler

    @cached_property
    def selected_application(self):
        # if 'application__pk' in self.kwargs:
        app = Application.objects.get(pk=self.kwargs['application__pk'])
        return app
        # return None
