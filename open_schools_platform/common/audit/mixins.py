# common/audit/mixins.py
from django.db import models
from .services import audit_logger
from .middleware import get_current_user


class AuditMixin(models.Model):
    """
    Миксин для автоматического аудита изменений модели
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Переопределяем save для логирования"""
        is_new = self._state.adding

        # Для существующих объектов получаем старое состояние
        if not is_new and self.pk:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                self._audit_old_instance = old_instance
            except self.__class__.DoesNotExist:
                self._audit_old_instance = None
        else:
            self._audit_old_instance = None

        # Вызываем оригинальный save
        result = super().save(*args, **kwargs)

        # Логируем после сохранения
        self._audit_log_save(is_new)

        return result

    def delete(self, *args, **kwargs):
        """Переопределяем delete для логирования"""
        # Логируем перед удалением
        self._audit_log_delete()

        # Вызываем оригинальный delete
        return super().delete(*args, **kwargs)

    def _audit_log_save(self, is_new):
        """Логирование операции сохранения"""
        try:
            user = get_current_user()

            if is_new:
                # Логирование создания
                audit_logger.log_create(self, user)
            elif hasattr(self, '_audit_old_instance') and self._audit_old_instance:
                # Логирование обновления с изменениями
                changes = self._audit_get_changes(self._audit_old_instance)
                if changes:  # Логируем только если есть изменения
                    audit_logger.log_update(self, user, changes=changes)
        except Exception as e:
            # Не падаем если аудит сломался
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Audit logging failed: {e}")
        finally:
            # Очищаем временные атрибуты
            if hasattr(self, '_audit_old_instance'):
                delattr(self, '_audit_old_instance')

    def _audit_log_delete(self):
        """Логирование удаления"""
        try:
            user = get_current_user()
            audit_logger.log_delete(self, user)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Audit logging failed on delete: {e}")

    def _audit_get_changes(self, old_instance):
        """Получение списка изменений"""
        changes = {}

        # Поля, которые не логируем
        exclude_fields = ['id', 'created_at', 'updated_at', 'deleted']

        for field in self._meta.fields:
            field_name = field.name

            if field_name in exclude_fields:
                continue

            old_value = getattr(old_instance, field_name)
            new_value = getattr(self, field_name)

            # Сравниваем значения
            if old_value != new_value:
                changes[field_name] = {
                    'old': str(old_value),
                    'new': str(new_value)
                }

        return changes