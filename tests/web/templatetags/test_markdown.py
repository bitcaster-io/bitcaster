from bitcaster.web.templatetags.markdown import markdown


def test_markdown():
    assert markdown('## Title')
