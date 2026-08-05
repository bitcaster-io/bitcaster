import pytest

from django.test import override_settings

from bitcaster.utils.widgets import SmartMedia


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_smart_media_absolute_path_debug() -> None:
    media = SmartMedia(js=["bitcaster/js/editor{min}.js"])
    assert "/static/bitcaster/js/editor.js" in media.render_js()[0]


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_smart_media_absolute_path_production() -> None:
    media = SmartMedia(js=["bitcaster/js/editor{min}.js"])
    assert "/static/bitcaster/js/editor.min.js" in media.render_js()[0]


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
def test_smart_media_combine_preserves_order() -> None:
    from django.forms.widgets import Media

    base = Media(js=["bitcaster/js/jquery.js"])
    media = SmartMedia.combine(base, js=["bitcaster/js/editor{min}.js"], css={"screen": ["bitcaster/css/app.css"]})
    assert isinstance(media, SmartMedia)
    assert "/static/bitcaster/js/jquery.js" in media.render_js()[0]
    assert "/static/bitcaster/js/editor.js" in media.render_js()[1]
    assert "bitcaster/css/app.css" in "".join(media.render_css())
