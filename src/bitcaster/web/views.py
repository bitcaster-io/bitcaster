from django.http import HttpRequest
from django.template.response import TemplateResponse


def index(request: "HttpRequest") -> TemplateResponse:
    return TemplateResponse(request, "bitcaster/index.html", {})
