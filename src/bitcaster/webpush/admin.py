from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from django.contrib.admin import register
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from bitcaster.admin.assignment import AssignmentAdmin
from bitcaster.models import Assignment
from bitcaster.webpush.models import Browser
from bitcaster.webpush.utils import sign

if TYPE_CHECKING:
    from django.http import HttpResponse


@register(Browser)
class BrowserAdmin(AssignmentAdmin):
    @button()
    def validate(self, request: HttpRequest, pk: str) -> "HttpResponse":
        asm: Assignment = self.get_object_or_404(request, pk)
        secret = sign(asm)
        url = reverse("webpush:ask", args=[secret])
        return HttpResponseRedirect(url)
