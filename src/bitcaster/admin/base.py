import logging

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin

logger = logging.getLogger(__name__)


class BaseAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin):
    pass
