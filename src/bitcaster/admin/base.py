import logging

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin

logger = logging.getLogger(__name__)

BUTTON_COLOR_LINK = "#96AA86"
BUTTON_COLOR_ACTION = "#2B44D6"
BUTTON_COLOR_LOCK = "#ba2121"
BUTTON_COLOR_UNLOCK = "green"


class BaseAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin):
    pass
