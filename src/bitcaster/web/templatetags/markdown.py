import markdown as md
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree

register = template.Library()


class LinksInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        if m.group(1).strip():
            label = m.group(1).strip()
            url = label
            a = etree.Element('a')
            a.text = label
            a.set('href', url)
            a.set('target', '_new')
        else:
            a = ''
        return a, m.start(0), m.end(0)


class SimpleLinkExtension(Extension):
    def extendMarkdown(self, md):
        self.md = md
        SIMPLELINK_RE = r'\[\[(.*)\]\]'
        wikilinkPattern = LinksInlineProcessor(SIMPLELINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.register(wikilinkPattern, 'simplelink', 75)


@register.filter()
@stringfilter
def markdown(value):
    return mark_safe(md.markdown(value, extensions=['markdown.extensions.fenced_code',
                                                    SimpleLinkExtension(),
                                                    ]))
