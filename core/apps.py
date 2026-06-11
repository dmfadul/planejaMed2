from django.apps import AppConfig
from django.db.backends.signals import connection_created

from .db.sqlite_collations import register_sqlite_collations


def register_collations(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        register_sqlite_collations(connection.connection)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals
        connection_created.connect(
            register_collations,
            dispatch_uid="core_register_sqlite_collations",
        )