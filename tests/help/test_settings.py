# mypy: disable-error-code="attr-defined"

from pytest_django.fixtures import SettingsWrapper

from django.test import RequestFactory


def test_doc_site_setting_default() -> None:
    from django.conf import settings

    assert settings.BITCASTER_DOCUMENTATION_SITE_URL == "https://docs.bitcaster.io"


def test_doc_site_setting_from_fragment(settings: SettingsWrapper) -> None:
    settings.BITCASTER_DOCUMENTATION_SITE_URL = "https://docs.example.com"
    from django.conf import settings as dj_settings

    assert dj_settings.BITCASTER_DOCUMENTATION_SITE_URL == "https://docs.example.com"


def test_version_context_processor_exposes_doc_site(settings: SettingsWrapper) -> None:
    from bitcaster.web.context_processors import version

    out = version(RequestFactory().get("/"))
    assert out["bitcaster"]["doc_site"] == "https://docs.bitcaster.io"

    settings.BITCASTER_DOCUMENTATION_SITE_URL = "https://docs.example.com"
    assert version(RequestFactory().get("/"))["bitcaster"]["doc_site"] == "https://docs.example.com"


def test_markdown_extension_uses_doc_site(settings: SettingsWrapper) -> None:
    from bitcaster.utils.markdown import BitcasterDocSiteExtension

    ext = BitcasterDocSiteExtension()
    assert ext.getConfigs()["base_url"] == "https://docs.bitcaster.io"

    settings.BITCASTER_DOCUMENTATION_SITE_URL = "https://docs.example.com"
    assert BitcasterDocSiteExtension().getConfigs()["base_url"] == "https://docs.example.com"
