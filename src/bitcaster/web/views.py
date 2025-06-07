import mimetypes
import posixpath
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseNotModified,
)
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils._os import safe_join
from django.utils.http import http_date
from django.utils.translation import gettext as _
from django.views import View
from django.views.static import directory_index, was_modified_since

if TYPE_CHECKING:
    from django.forms import Form


def index(request: "HttpRequest") -> TemplateResponse:
    return TemplateResponse(request, "bitcaster/index.html", {})


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


class LoginView(BaseLoginView):
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        return reverse_lazy("home")

    def form_invalid(self, form: "Form") -> HttpResponse:
        messages.error(self.request, "Invalid username or password")
        return self.render_to_response(self.get_context_data(form=form))
