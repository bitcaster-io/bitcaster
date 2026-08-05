import pytest

from django.forms.widgets import Media
from django.test import override_settings

from bitcaster.utils.widgets import SmartMedia


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_absolute_path_debug() -> None:
    media = SmartMedia(js=["bitcaster/js/editor{min}.js"])
    assert media.absolute_path("bitcaster/js/editor{min}.js") == "/static/bitcaster/js/editor.js"
    assert "/static/bitcaster/js/editor.js" in media.render_js()[0]


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_smart_media_absolute_path_production() -> None:
    media = SmartMedia(js=["bitcaster/js/editor{min}.js"])
    assert media.absolute_path("bitcaster/js/editor{min}.js") == "/static/bitcaster/js/editor.min.js"
    assert "/static/bitcaster/js/editor.min.js" in media.render_js()[0]


@pytest.mark.django_db
@override_settings(DEBUG=False)
@pytest.mark.parametrize(
    "path",
    [
        "http://cdn.example.com/editor.js",
        "https://cdn.example.com/editor.min.js",
        "/absolute/path/editor.js",
    ],
)
def test_smart_media_absolute_path_external_untouched(path: str) -> None:
    media = SmartMedia()
    assert media.absolute_path(path) == path


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_absolute_path_without_min() -> None:
    media = SmartMedia()
    assert media.absolute_path("bitcaster/js/plain.js") == "/static/bitcaster/js/plain.js"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_add_preserves_type() -> None:
    media = SmartMedia(js=["bitcaster/js/editor{min}.js"], css={"screen": ["bitcaster/css/app.css"]}) + SmartMedia(
        js=["bitcaster/js/other.js"], css={"screen": ["bitcaster/css/other.css"]}
    )
    assert isinstance(media, SmartMedia)
    assert "/static/bitcaster/js/editor.js" in media.render_js()[0]
    assert "/static/bitcaster/js/other.js" in media.render_js()[1]
    assert "bitcaster/css/app.css" in "".join(media.render_css())
    assert "bitcaster/css/other.css" in "".join(media.render_css())


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_add_deduplicates_js() -> None:
    media = SmartMedia(js=["bitcaster/js/editor{min}.js"]) + SmartMedia(
        js=["bitcaster/js/editor{min}.js", "bitcaster/js/other.js"]
    )
    rendered = "".join(media.render_js())
    assert rendered.count("/static/bitcaster/js/editor.js") == 1
    assert "/static/bitcaster/js/other.js" in rendered


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_add_deduplicates_css() -> None:
    media = SmartMedia(css={"screen": ["bitcaster/css/app.css"]}) + SmartMedia(
        css={"screen": ["bitcaster/css/app.css", "bitcaster/css/other.css"]}
    )
    rendered = "".join(media.render_css())
    assert rendered.count("bitcaster/css/app.css") == 1
    assert "bitcaster/css/other.css" in rendered


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_add_plain_media_rhs() -> None:
    media = SmartMedia(js=["bitcaster/js/editor{min}.js"]) + Media(js=["bitcaster/js/editor{min}.js", "jquery.js"])
    assert isinstance(media, SmartMedia)
    rendered = "".join(media.render_js())
    assert rendered.count("/static/bitcaster/js/editor.js") == 1
    assert "/static/jquery.js" in rendered


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_add_empty_other_returns_clone() -> None:
    left = SmartMedia(js=["bitcaster/js/editor{min}.js"])
    media = left + SmartMedia()
    assert isinstance(media, SmartMedia)
    assert media.render_js() == left.render_js()


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_combine_preserves_order() -> None:
    base = Media(js=["bitcaster/js/jquery.js"])
    media = SmartMedia.combine(base, js=["bitcaster/js/editor{min}.js"], css={"screen": ["bitcaster/css/app.css"]})
    assert isinstance(media, SmartMedia)
    assert "/static/bitcaster/js/jquery.js" in media.render_js()[0]
    assert "/static/bitcaster/js/editor.js" in media.render_js()[1]
    assert "bitcaster/css/app.css" in "".join(media.render_css())


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_combine_no_extras_clones() -> None:
    base = Media(js=["bitcaster/js/jquery.js"], css={"screen": ["bitcaster/css/app.css"]})
    media = SmartMedia.combine(base)
    assert isinstance(media, SmartMedia)
    assert media.render_js() == SmartMedia(js=["bitcaster/js/jquery.js"]).render_js()
    assert "bitcaster/css/app.css" in "".join(media.render_css())


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_combine_empty_extras_ignored() -> None:
    base = Media(js=["bitcaster/js/jquery.js"])
    media = SmartMedia.combine(base, js=[], css={})
    assert isinstance(media, SmartMedia)
    assert len(media._js_lists) == 1
    assert len(media._css_lists) == 1


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_combine_does_not_mutate_source() -> None:
    base = Media(js=["bitcaster/js/jquery.js"])
    SmartMedia.combine(base, js=["bitcaster/js/editor{min}.js"])
    assert base.render_js() == ['<script src="/static/bitcaster/js/jquery.js"></script>']


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_combine_with_smartmedia_source() -> None:
    base = SmartMedia(js=["bitcaster/js/editor{min}.js"])
    media = SmartMedia.combine(base, js=["bitcaster/js/other.js"])
    assert isinstance(media, SmartMedia)
    rendered = "".join(media.render_js())
    assert "/static/bitcaster/js/editor.js" in rendered
    assert "/static/bitcaster/js/other.js" in rendered
