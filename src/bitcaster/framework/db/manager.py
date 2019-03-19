# -*- coding: utf-8 -*-
import logging

from .fields import DeletionStatus

logger = logging.getLogger(__name__)


class DeleteableModelManagerMixin:
    def valid(self, *args, **kwargs):
        return super().filter(status=DeletionStatus.ACTIVE).filter(*args, **kwargs)
