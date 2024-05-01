import enum
import logging

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin

logger = logging.getLogger(__name__)


class ButtonColor(enum.Enum):
    LINK = "#96AA86"
    ACTION = "#2B44D6"
    LOCK = "#ba2121"
    UNLOCK = "green"


class BaseAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin):
    pass
