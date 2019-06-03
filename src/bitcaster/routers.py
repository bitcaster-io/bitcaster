

class DBLogRouter(object):
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'crashlog':
            return 'crashlog'

    def db_for_read(self, model, **hints):
        return self.db_for_write(model, **hints)

    def allow_syncdb(self, db, model):
        if model._meta.app_label == 'crashlog' and db != 'crashlog':
            return False
