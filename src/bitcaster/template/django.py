from django.template import Engine, Template as _Template


class Engine2(Engine):
    default_builtins = [
        # 'django.template.defaulttags',
        'django.template.defaultfilters',
        # 'django.template.loader_tags',
        'django.templatetags.tz',
        'bitcaster.template.messagefilters',
    ]

    def __init__(self, dirs=None, app_dirs=False, context_processors=None,
                 debug=False, loaders=None, string_if_invalid='',
                 file_charset='utf-8', libraries=None, builtins=None, autoescape=True):
        super(Engine2, self).__init__(dirs, app_dirs, context_processors,
                                      debug, loaders, string_if_invalid,
                                      file_charset, libraries, builtins, autoescape)


class Template(_Template):

    def __init__(self, template_string, origin=None, name=None, engine=None):
        engine = Engine2()
        super().__init__(template_string, origin, name, engine)
