from django.contrib.auth.models import Group as DjangoGroup
from django.utils.translation import gettext as _


class Group(DjangoGroup):
    class Meta:
        proxy = True
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
