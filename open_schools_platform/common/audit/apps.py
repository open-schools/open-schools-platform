# common/audit/apps.py
from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'open_schools_platform.common.audit'
    verbose_name = 'Аудит действий'

    def ready(self):
        """Инициализация приложения"""
        # Можно импортировать сигналы здесь
        import open_schools_platform.common.audit.signals