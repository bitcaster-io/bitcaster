from admin_extra_urls.extras import ExtraUrlMixin, link
from admin_extra_urls.mixins import _confirm_action


class TruncateTableMixin(ExtraUrlMixin):

    def _truncate(self, request):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('TRUNCATE TABLE "{0}" CASCADE '.format(self.model._meta.db_table))

    @link(label='Truncate', permission=lambda request, obj: request.user.is_superuser)
    def truncate(self, request):
        return _confirm_action(self, request, self._truncate, 'Continuing will erase the entire content of the table.',
                               'Successfully executed', )
