from django.conf import settings
from django.forms.widgets import Media, static


class SmartMedia(Media):
    def absolute_path(self, path: str) -> str:
        if settings.DEBUG:
            v = ""
        else:
            v = ".min"
        path = path.replace("{min}", v)
        if path.startswith(("http://", "https://", "/")):
            return path
        return static(path)

    def __add__(self, other: Media) -> "SmartMedia":
        combined = SmartMedia()
        combined._css_lists = self._css_lists[:]
        combined._js_lists = self._js_lists[:]
        for item in other._css_lists:
            if item and item not in self._css_lists:
                combined._css_lists.append(item)
        for item in other._js_lists:
            if item and item not in self._js_lists:
                combined._js_lists.append(item)
        return combined

    @classmethod
    def combine(
        cls, media: Media, *, js: list[str] | None = None, css: dict[str, list[str]] | None = None
    ) -> "SmartMedia":
        combined = cls()
        combined._css_lists = media._css_lists[:]
        combined._js_lists = media._js_lists[:]
        if js:
            combined._js_lists.append(js)
        if css:
            combined._css_lists.append(css)
        return combined
