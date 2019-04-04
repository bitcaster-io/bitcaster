import logging

from rest_framework.renderers import HTMLFormRenderer

from bitcaster.api.fields import PasswordField

logger = logging.getLogger(__name__)


class BitcasterHTMLFormRenderer(HTMLFormRenderer):
    # custom_style = ClassLookupDict({
    #     PasswordField: {
    #         'base_template': 'password.html',
    #         'input_type': 'password'
    #     },
    # })

    def __init__(self) -> None:
        self.default_style[PasswordField] = {'base_template': 'password.html',
                                             'input_type': 'password'}
        super().__init__()

    # def render_field(self, field, parent_style):
    #     if isinstance(field._field, serializers.HiddenField):
    #         return ''
    #     try:
    #         style = dict(self.custom_style[field])
    #     except KeyError:
    #         style = dict(self.default_style[field])
    #
    #     style.update(field.style)
    #     if 'template_pack' not in style:
    #         style['template_pack'] = parent_style.get('template_pack', self.template_pack)
    #     style['renderer'] = self
    #
    #     # Get a clone of the field with text-only value representation.
    #     field = field.as_form_field()
    #
    #     if style.get('input_type') == 'datetime-local' and isinstance(field.value, str):
    #         field.value = field.value.rstrip('Z')
    #
    #     if 'template' in style:
    #         template_name = style['template']
    #     else:
    #         template_name = style['template_pack'].strip('/') + '/' + style['base_template']
    #
    #     template = loader.get_template(template_name)
    #     context = {'field': field, 'style': style}
    #     return template.render(context)
