# -*- coding: utf-8 -*-
"""
mercury / utils
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import json
import logging

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from rest_framework.exceptions import ValidationError as DRFValidationError
from strategy_field.utils import import_by_name

from mercury.utils.language import flatten

logger = logging.getLogger(__name__)


class ValidateJsonMixin(object):
    def clean(self):
        handler_class = self.cleaned_data.get('handler', None)
        config = self.cleaned_data.get('config', {})
        enabled = self.cleaned_data.get('enabled', False)

        if handler_class and enabled:
            try:
                handler = import_by_name(handler_class)
            except DRFValidationError as e:
                raise ValidationError(e)
            if not config:
                config = handler.defaults()
            else:
                config = {**handler.defaults(), **config}
            valid, errors = handler.validate_configuration(config, False)
            # Ugly but it is the only way
            d = self.data.copy()
            d['config'] = json.dumps(config)
            self.data = d
            if not valid:
                ret = []
                for k, v in errors.items():
                    ret.append("<b>{0}</b>:{1} ".format(k, ",".join(flatten(v))))
                raise ValidationError({'config': mark_safe(" ".join(flatten(ret)))})

        return super().clean()
