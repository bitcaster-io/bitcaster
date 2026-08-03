# mypy: disable-error-code="attr-defined"
from typing import Any

from pathlib import Path

import pytest

from django.core import checks as django_checks
from django.test import override_settings

from bitcaster.help.checks import E001, E002, E003


def _errors(monkeypatch: pytest.MonkeyPatch, links: dict[str, str], tmp_path: Path) -> list[Any]:
    from bitcaster.help import checks as help_checks

    monkeypatch.setattr(help_checks, "HELP_LINKS", links)
    with override_settings(PROJECT_ROOT=str(tmp_path)):
        return django_checks.run_checks(tags=["help"])


def test_valid_mapping_no_errors() -> None:
    assert django_checks.run_checks(tags=["help"]) == []


def test_missing_doc_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    errors = _errors(monkeypatch, {"^/x/": "adm-guide/app/"}, tmp_path)
    assert [e.id for e in errors] == [E001.id]


def test_leaf_page_via_md_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    (docs / "adm-guide").mkdir(parents=True)
    (docs / "adm-guide" / "app.md").write_text("# App")
    assert _errors(monkeypatch, {"^/x/": "adm-guide/app/"}, tmp_path) == []


def test_section_page_via_pages_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    (docs / "adm-guide").mkdir(parents=True)
    (docs / "adm-guide" / ".pages").write_text("")
    assert _errors(monkeypatch, {"^/x/": "adm-guide/"}, tmp_path) == []


def test_section_page_via_index_md(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    (docs / "adm-guide").mkdir(parents=True)
    (docs / "adm-guide" / "index.md").write_text("# Guide")
    assert _errors(monkeypatch, {"^/x/": "adm-guide/"}, tmp_path) == []


@pytest.mark.parametrize(
    "doc_path",
    [
        pytest.param("/absolute/", id="leading-slash"),
        pytest.param("adm-guide/app#anchor/", id="anchor"),
        pytest.param("adm-guide/app.md", id="md-extension"),
    ],
)
def test_invalid_doc_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, doc_path: str) -> None:
    (tmp_path / "docs").mkdir()
    errors = _errors(monkeypatch, {"^/x/": doc_path}, tmp_path)
    assert [e.id for e in errors] == [E002.id]


def test_invalid_regex(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    errors = _errors(monkeypatch, {"[": "adm-guide/app/"}, tmp_path)
    assert [e.id for e in errors] == [E003.id]


def test_skipped_when_docs_dir_absent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert _errors(monkeypatch, {"^/x/": "adm-guide/app/"}, tmp_path) == []


def test_root_checks_module_untouched() -> None:
    root_checks = Path(__file__).resolve().parents[2] / "src" / "bitcaster" / "checks.py"
    content = root_checks.read_text()
    assert "bitcaster.help." not in content
