from bitcaster.web.templatetags.markdown import markdown


def test_markdown():
    assert markdown('## Title')


def test_markdown_href():
    assert markdown('[[http://bitcaster.io]]') == '<p><a href="http://bitcaster.io">http://bitcaster.io</a></p>'
