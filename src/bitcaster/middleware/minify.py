import logging
import re
from enum import IntFlag, unique
from typing import TYPE_CHECKING, Any, Awaitable, Optional

from constance import config
from constance.signals import config_updated
from django.conf import settings
from django.http import HttpRequest, HttpResponseBase
from django.utils.functional import cached_property
from htmlmin.main import Minifier

if TYPE_CHECKING:
    from bitcaster.types.http import (
        AnyRequest,
        AnyResponse,
        AsyncGetResponseCallable,
        GetResponseCallable,
    )


logger = logging.getLogger(__name__)


@unique
class MinifyFlag(IntFlag):
    HTML: int = 1
    NEWLINE: int = 2
    SPACES: int = 4


class HtmlMinMiddleware:
    get_response: "GetResponseCallable | AsyncGetResponseCallable"

    def __init__(self, get_response: "GetResponseCallable | AsyncGetResponseCallable") -> None:
        self.get_response = get_response
        self.minifier = Minifier(
            remove_comments=True,
            remove_empty_space=True,
            remove_all_empty_space=True,
            remove_optional_attribute_quotes=True,
            reduce_empty_attributes=True,
        )
        config_updated.connect(self.update_config)

    @cached_property
    def config_value(self) -> int:
        return int(config.MINIFY_RESPONSE)

    @cached_property
    def ignore_regex(self) -> Optional[re.Pattern[str]]:
        if config.MINIFY_IGNORE_PATH:
            return re.compile(config.MINIFY_IGNORE_PATH)

    def update_config(self, sender: Any, key: str, old_value: Any, new_value: Any, **kwargs: Any) -> None:
        if hasattr(self, "config_value"):  # pragma: no cover
            del self.config_value

        if hasattr(self, "ignore_regex"):  # pragma: no cover
            del self.ignore_regex

    def ignore_path(self, path: str) -> bool:
        if self.ignore_regex:
            return bool(self.ignore_regex.match(path))

    def can_minify(self, request: "AnyRequest", response: "AnyResponse") -> bool:
        return (
            "Content-Type" in response
            and "text/html" in response["Content-Type"]
            and "admin/" not in request.path_info
            and not hasattr(request, "no_minify")
            and not self.ignore_path(request.path_info)
            and not request.headers.get("X-No-Minify")
        )

    def __call__(self, request: HttpRequest) -> "HttpResponseBase | Awaitable[HttpResponseBase]":
        response = self.get_response(request)
        if not response.streaming and len(response.content) < 200:
            return response

        if self.can_minify(request, response):
            if bool(self.config_value & MinifyFlag.HTML):
                response.content = self.minifier.minify(response.content.decode()).encode()
                response.content = response.content.replace(b"\n", b"")
            if bool(self.config_value & MinifyFlag.NEWLINE):
                response.content = response.content.replace(b"\n", b"")
            if bool(self.config_value & MinifyFlag.SPACES):
                s = response.content
                while b"  " in s:
                    s = s.replace(b"  ", b" ")
                response.content = s
            response.headers["Content-Length"] = str(len(response.content))
        elif settings.DEBUG:
            logger.warn(f'Skip minification of "{request.path_info}"')
        return response
