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
    HttpResponseRedirect,
)
from django.http.response import HttpResponseBadRequest
from django.urls import reverse_lazy
from django.utils._os import safe_join
from django.utils.http import http_date
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import ContextMixin, TemplateView
from django.views.static import directory_index, was_modified_since
from unfold.sites import UnfoldAdminSite

from bitcaster.exceptions import DecryptionError, KeyExpiredError
from bitcaster.models import Attachment, Occurrence
from bitcaster.utils.security import KeyManager


class UnfoldViewMixin(UnfoldAdminSite, ContextMixin):
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            colors=self._get_colors("COLORS", self.request),
        )
        return ctx


class IndexView(UnfoldViewMixin, TemplateView):
    template_name = "bitcaster/index.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user_agent.is_mobile:
            return HttpResponseRedirect(reverse_lazy("pwa:index"))
        return super().get(request, *args, **kwargs)


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


class SafeAttachmentDownloadView(View):
    def get(self, request: HttpRequest, key: str) -> HttpResponse | FileResponse:
        try:
            parts = KeyManager().parse_key(key)
            attachment = Attachment.objects.get(correlation_id=parts["correlation_id"])
        except DecryptionError:
            return HttpResponseBadRequest(_("Malformed download key."))
        except KeyExpiredError as e:
            return HttpResponseBadRequest(str(e))
        except Attachment.DoesNotExist as e:
            raise Http404(_("No attachment found for this key.")) from e

        return FileResponse(attachment.document, content_type=attachment.mime_type, as_attachment=True)


class RecipientsView(UnfoldViewMixin, TemplateView):
    """Display the list of recipients, for a specific occurrence."""

    template_name = "bitcaster/recipients.html"

    def validate_token(self) -> dict[str, str | int]:
        return KeyManager().parse_key(self.kwargs["token"])

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        parts = self.validate_token()
        occurrence = Occurrence.objects.select_related("event__application").get(pk=parts["occurrence"])
        kwargs["occurrence"] = occurrence
        kwargs["parts"] = parts
        kwargs["data"] = occurrence.collect_recipients()
        return super().get_context_data(**kwargs)
