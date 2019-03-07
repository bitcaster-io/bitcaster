
class SidebarMixin:

    def get_context_data(self, **kwargs):
        sidebar_class = self.request.COOKIES.get('sidebar')
        return super().get_context_data(sidebar=sidebar_class, **kwargs)
