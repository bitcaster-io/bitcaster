import markdown as md
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from markdown import Extension
from markdown.extensions.wikilinks import WikiLinksInlineProcessor

register = template.Library()


def build_url(label, base, end):
    return label


class SimpleLinkExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'base_url': ['', 'String to append to beginning or URL.'],
            'end_url': ['', 'String to append to end of URL.'],
            'html_class': ['', 'CSS hook. Leave blank for none.'],
            'build_url': [build_url, 'Callable formats URL from label.'],
        }
        super(SimpleLinkExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        self.md = md
        SIMPLELINK_RE = r'\[\[(.*)\]\]'
        wikilinkPattern = WikiLinksInlineProcessor(SIMPLELINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.register(wikilinkPattern, 'simplelink', 75)


@register.filter()
@stringfilter
def markdown(value):
    return mark_safe(md.markdown(value, extensions=['markdown.extensions.fenced_code',
                                                    SimpleLinkExtension(),
                                                    ]))
