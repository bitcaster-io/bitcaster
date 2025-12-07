from django.contrib.admin.utils import quote
from django.urls import reverse
from unfold.views import ChangeList


class MultiAdminChangeList(ChangeList):
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse(
            "%s:%s_%s_change" % (self.model_admin.admin_site.name, self.opts.app_label, self.opts.model_name),
            args=(quote(pk),),
            current_app=self.model_admin.admin_site.name,
        )
