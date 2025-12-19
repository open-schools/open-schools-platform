# common/audit/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    """Автоматическое логирование создания и обновления моделей"""
    # Исключаем сами модели аудита и пользователей
    if sender.__name__ in ['AuditLog', 'User']:
        return

    # Определяем действие
    action = 'create' if created else 'update'

    # Определяем пользователя (нужно передавать через request)
    # Для автоматического логирования лучше использовать middleware

    # Логируем только если модель имеет метод log_event
    if hasattr(instance, 'log_event'):
        user = getattr(instance, '_current_user', None)
        changes = getattr(instance, '_changed_fields', {})

        instance.log_event(
            event_type=action,
            user=user,
            description=f"{action.capitalize()} {instance._meta.verbose_name}",
            metadata={'changes': changes}
        )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Автоматическое логирование удаления моделей"""
    if sender.__name__ in ['AuditLog', 'User']:
        return

    if hasattr(instance, 'log_event'):
        user = getattr(instance, '_current_user', None)

        instance.log_event(
            event_type='delete',
            user=user,
            description=f"Delete {instance._meta.verbose_name}"
        )