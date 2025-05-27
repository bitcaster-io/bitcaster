import re
import xml.etree.ElementTree as ET  # nosec
from typing import Any

from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

from bitcaster.config import env


def build_url(base: str, path: str) -> str:
    clean_label = re.sub(r"([ ]+_)|(_[ ]+)|([ ]+)", "_", path)
    return f"{base}/{clean_label}"


class LinksInlineProcessor(InlineProcessor):
    def __init__(self, pattern: str, config: dict[str, Any]):
        super().__init__(pattern)
        self.config = config

    def handleMatch(  # type: ignore[override]  # noqa: N802
        self, m: re.Match[str], data: str
    ) -> tuple[ET.Element | str | None, int | None, int | None]:
        base_url = self.config.get("base_url", "/")
        parts = m.groups()[:]
        path = parts[0]
        label = parts[1].strip() or path
        url = build_url(base_url, path)
        a = ET.Element("a")
        a.text = label
        a.set("href", url)
        return a, m.start(0), m.end(0)


class BitcasterDocSiteExtension(Extension):
    def __init__(self, **kwargs: Any):
        self.config = {
            "base_url": [env("BITCASTER_DOCUMENTATION_SITE_URL"), ""],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:  #  noqa: N802
        link_re = r"\[\[doc:([\w\/]+):?(\w*)\]\]"
        proc = LinksInlineProcessor(link_re, self.getConfigs())
        proc.md = md
        md.inlinePatterns.register(proc, "bcdoc", 75)
