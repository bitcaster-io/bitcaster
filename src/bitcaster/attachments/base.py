from _md5 import md5
from io import BytesIO
from urllib.parse import urlencode

from django.utils.functional import cached_property
from jinja2 import Template, environment
from rest_framework import serializers
from rest_framework.fields import empty
from slugify import slugify

from bitcaster import get_full_version
from bitcaster.configurable import ConfigurableMixin
from bitcaster.utils.language import get_attr

environment.DEFAULT_FILTERS['md5'] = lambda s: md5(s.encode('utf-8'))
environment.DEFAULT_FILTERS['hexdigest'] = lambda s: s.hexdigest()
environment.DEFAULT_FILTERS['urlencode'] = urlencode
environment.DEFAULT_FILTERS['slugify'] = slugify


class Parser:
    name = 'Plain'

    @classmethod
    def parse(self, tpl, ctx):
        return tpl


class BasicParser(Parser):
    name = 'Basic'

    @classmethod
    def parse(self, tpl, ctx):
        pass


class ExtendedParser(Parser):
    name = 'Extended'

    @classmethod
    def parse(self, tpl, ctx):
        pass


class JinjaParser(Parser):
    name = 'Jinja'

    @classmethod
    def parse(self, tpl, ctx):
        template = Template(tpl)
        return template.render(**ctx)


class Attachment:
    def __init__(self, name: str, content: BytesIO, content_type=None):
        self.name = name
        self.content = content
        self.content_type = content_type

    def read(self):
        self.content.seek(0)
        return self.content.read()


class RetrieverOptions(serializers.Serializer):
    PARSER_PLAIN = 0
    PARSER_BASIC = 1
    PARSER_EXTENDED = 2
    PARSER_JINJA = 3
    PARSERS = {PARSER_PLAIN: Parser,
               # PARSER_BASIC: BasicParser,
               # PARSER_EXTENDED: ExtendedParser,
               PARSER_JINJA: JinjaParser}

    parser = serializers.ChoiceField([(i, n.name) for i, n in PARSERS.items()], default=1)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)


class BaseRetriever(ConfigurableMixin):
    options_class = RetrieverOptions
    icon = 'paperclip.png'
    __version__ = get_full_version()

    @cached_property
    def parser(self):
        return self.options_class.PARSERS[self.config['parser']]

    def parse_name(self, **extra):
        context = {}
        context.update(extra)
        return self.parser.parse(self.config['name_pattern'], context)

    def parse_template(self, **extra):
        context = {}
        context.update(extra)
        return self.parser.parse(self.config['url_pattern'], context)

    def get_options_form(self, **kwargs):
        self.application = kwargs.pop('application', get_attr(self, 'owner.application'))
        if not kwargs.get('data', None):
            kwargs['data'] = empty
        form = super().get_options_form(**kwargs)
        return form

    def get(self, subscription) -> Attachment:
        raise NotImplementedError
