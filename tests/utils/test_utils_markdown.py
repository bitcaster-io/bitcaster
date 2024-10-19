import markdown
import pytest

from bitcaster.utils.markdown import BitcasterDocSiteExtension


@pytest.mark.parametrize(
    "value,expected",
    [
        ("[[doc:path]]", '<p><a href="http://doc/path">path</a></p>'),
        ("[[doc:path:label]]", '<p><a href="http://doc/path">label</a></p>'),
        ("[[doc:]]", "<p>[[doc:]]</p>"),
        ("[[doc:a:b:c]]", "<p>[[doc:a:b:c]]</p>"),
        ("[[doc]]", "<p>[[doc]]</p>"),
    ],
)
def test_processor(value: str, expected: str) -> None:
    assert (
        markdown.markdown(
            value,
            extensions=[
                BitcasterDocSiteExtension(base_url="http://doc"),
            ],
        )
        == expected
    )
