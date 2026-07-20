# class EcommerceRouter:
#     # admin_management app-er sob kisu admin_db-te jabe
#     route_app_labels = {'admin_management', 'admin', 'auth', 'contenttypes', 'sessions'}

#     def db_for_read(self, model, **hints):
#         if model._meta.app_label in self.route_app_labels:
#             return 'admin_db'
#         return 'default'

#     def db_for_write(self, model, **hints):
#         if model._meta.app_label in self.route_app_labels:
#             return 'admin_db'
#         return 'default'

#     def allow_relation(self, obj1, obj2, **hints):
#         return True

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         if app_label in self.route_app_labels:
#             return db == 'admin_db'
#         return db == 'default'