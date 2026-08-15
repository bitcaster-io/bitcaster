from __future__ import annotations

from typing import Iterator

import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.sax.saxutils import quoteattr

import requests
from lxml import html

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_CHANGE_PATHS = ("docs/", "properdocs.yml", "tests/docs/")
DOCS_TEST_FLAG = "RUN_DOCS_TESTS"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _docs_changed() -> bool:
    try:
        base = _git("merge-base", "origin/develop", "HEAD")
        changed = _git("diff", "--name-only", base, "HEAD").splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return True
    return any(path.startswith(prefix) for path in changed for prefix in DOCS_CHANGE_PATHS)


def _can_run() -> bool:
    if os.getenv(DOCS_TEST_FLAG) == "1":
        return True
    return shutil.which("properdocs") is not None and _docs_changed()


pytestmark = pytest.mark.skipif(
    not _can_run(),
    reason="docs not changed (docs/ or properdocs.yml) or properdocs not installed",
)


@pytest.fixture(scope="session")
def docs_site(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    site_dir = tmp_path_factory.mktemp("docs") / "site"
    env = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")}
    subprocess.run(
        ["properdocs", "build", "-d", str(site_dir)],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return site_dir


SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
SKIP_HOSTS = {"bitcaster-io.slack.com"}  # Slack workspaces require auth and return 403 to bots
SKIP_DIRS = {"_theme"}
PLACEHOLDER_HOSTS = {"SERVER_ADDRESS", "bitcaster.yourdomain.com"}
PLACEHOLDER_HOST_RE = re.compile(r"[<>]")


def _site_url_path() -> str:
    content = (PROJECT_ROOT / "properdocs.yml").read_text(encoding="utf-8")
    match = re.search(r"^site_url:\s*(\S+)", content, flags=re.MULTILINE)
    return urlparse(match.group(1)).path.strip("/") if match else ""


def _site_url_host() -> str:
    content = (PROJECT_ROOT / "properdocs.yml").read_text(encoding="utf-8")
    match = re.search(r"^site_url:\s*(\S+)", content, flags=re.MULTILINE)
    return urlparse(match.group(1)).hostname or "" if match else ""


def _iter_links(site_dir: Path):
    for page in sorted(site_dir.rglob("*.html")):
        if page.relative_to(site_dir).parts[0] in SKIP_DIRS:
            continue
        tree = html.parse(str(page))
        for el in tree.xpath("//a[@href] | //img[@src] | //script[@src] | //link[@href] | //iframe[@src]"):
            url = el.get("href") or el.get("src")
            if url:
                yield page, tree, url


def _has_anchor(tree, anchor: str) -> bool:
    q = quoteattr(anchor)
    return bool(tree.xpath(f"//*[@id={q}]") or tree.xpath(f"//*[@name={q}]"))


def _resolve_target(site_dir: Path, page: Path, path: str, site_url_path: str = "") -> Path | None:
    path = unquote(path)
    if path.startswith("/"):
        if site_url_path and path.lstrip("/").startswith(site_url_path):
            path = path.lstrip("/")[len(site_url_path) :]
        target = site_dir / path.lstrip("/")
    else:
        target = (page.parent / path).resolve()
    if target.is_dir():
        target = target / "index.html"
    if not target.exists():
        alt = target.with_suffix(".html")
        if alt.exists():
            return alt
        return None
    return target


def _is_placeholder(url: str) -> bool:
    host = urlparse(url).hostname
    return bool(host and (host.upper() in PLACEHOLDER_HOSTS or PLACEHOLDER_HOST_RE.search(host)))


def test_internal_links(docs_site: Path) -> None:
    errors: list[str] = []
    site_url_path = _site_url_path()
    for page, tree, url in _iter_links(docs_site):
        if url.startswith(SKIP_SCHEMES) or url.startswith(("http://", "https://")):
            continue
        parsed = urlparse(url)
        if not parsed.path:
            if parsed.fragment and not _has_anchor(tree, parsed.fragment):
                errors.append(f"{page.relative_to(docs_site)}: missing anchor #{parsed.fragment} in same page")
            continue
        target = _resolve_target(docs_site, page, parsed.path, site_url_path)
        if target is None:
            errors.append(f"{page.relative_to(docs_site)}: broken link {url!r}")
            continue
        if parsed.fragment and not _has_anchor(html.parse(str(target)), parsed.fragment):
            errors.append(
                f"{page.relative_to(docs_site)}: missing anchor #{parsed.fragment} in {target.relative_to(docs_site)}"
            )
    assert not errors, "\n".join(errors)


def test_external_links(docs_site: Path) -> None:
    errors: list[str] = []
    session = requests.Session()
    seen: set[str] = set()
    self_host = _site_url_host()
    for page, _tree, url in _iter_links(docs_site):
        if not url.startswith(("http://", "https://")):
            continue
        if _is_placeholder(url) or urlparse(url).hostname in SKIP_HOSTS:
            continue
        if urlparse(url).hostname == self_host:
            continue
        if url in seen:
            continue
        seen.add(url)
        try:
            response = session.get(url, timeout=15, allow_redirects=True, stream=True)
            response.close()
            if response.status_code >= 400:
                errors.append(f"{page.relative_to(docs_site)}: {url} -> HTTP {response.status_code}")
        except requests.RequestException as exc:
            errors.append(f"{page.relative_to(docs_site)}: {url} -> {type(exc).__name__}: {exc}")
    assert not errors, "\n".join(errors)
