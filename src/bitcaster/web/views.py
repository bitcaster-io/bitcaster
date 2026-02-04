import mimetypes
import posixpath
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseNotModified,
)
from django.utils._os import safe_join
from django.utils.http import http_date
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import ContextMixin, TemplateView
from django.views.static import directory_index, was_modified_since
from unfold.sites import UnfoldAdminSite


class UnfoldViewMixin(UnfoldAdminSite, ContextMixin):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            colors=self._get_colors("COLORS", self.request),
        )
        return ctx


class IndexView(UnfoldViewMixin, TemplateView):
    template_name = "bitcaster/index.html"


class LogoutView(BaseLogoutView):
    def get_success_url(self) -> str:
        return "/"


class HealthCheckView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("Ok")


class MediaView(View):
    def get(self, request: HttpRequest, path: str) -> HttpResponse | FileResponse:
        path = posixpath.normpath(path).lstrip("/")
        fullpath = Path(safe_join(settings.MEDIA_ROOT, path))
        if fullpath.is_dir():
            if settings.DEBUG:  # pragma: no cover
                return directory_index(path, fullpath)
            raise Http404(_("Directory indexes are not allowed here."))
        if not fullpath.exists():
            raise Http404(_("“%(path)s” does not exist") % {"path": fullpath})
        # Respect the If-Modified-Since header.
        statobj = fullpath.stat()
        if not was_modified_since(request.META.get("HTTP_IF_MODIFIED_SINCE"), statobj.st_mtime):
            return HttpResponseNotModified()
        content_type, __ = mimetypes.guess_type(str(fullpath))
        content_type = content_type or "application/octet-stream"
        response = FileResponse(fullpath.open("rb"), content_type=content_type)
        response.headers["Last-Modified"] = http_date(statobj.st_mtime)
        return response
