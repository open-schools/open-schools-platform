# common/audit/services.py
import logging

from django.contrib.contenttypes.models import ContentType

from .models import AuditLog, AuditEventType

logger = logging.getLogger(__name__)


class AuditLogger:
    """Универсальный сервис для логирования"""

    @staticmethod
    def log_event(
            event_type: str,
            user=None,
            content_object=None,
            app=None,
            organization=None,
            description="",
            metadata=None,
            ip_address=None,
            user_agent=None,
            request=None
    ):
        """
        Создание записи в журнале аудита
        """
        try:
            # Получаем пользователя из request если не передан
            if request and hasattr(request, 'user') and request.user.is_authenticated and not user:
                user = request.user

            # Получаем IP из request
            if request and not ip_address:
                ip_address = AuditLogger._get_client_ip(request)

            # Получаем User-Agent
            if request and not user_agent:
                user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Определяем content_type и object_id
            content_type = None
            object_id = None
            if content_object:
                content_type = ContentType.objects.get_for_model(content_object)
                object_id = str(content_object.pk)

            # Автоматически заполняем app и organization из content_object
            if content_object and not app:
                # Проверяем, является ли объект приложением
                if hasattr(content_object, '_meta') and content_object._meta.model_name == 'app':
                    app = content_object
                # Или содержит ссылку на приложение
                elif hasattr(content_object, 'app'):
                    app = content_object.app

            if content_object and not organization:
                # Проверяем, является ли объект организацией
                if hasattr(content_object, '_meta') and content_object._meta.model_name == 'organization':
                    organization = content_object
                # Или содержит ссылку на организацию
                elif hasattr(content_object, 'organization'):
                    organization = content_object.organization

            # Создаем запись
            audit_log = AuditLog.objects.create(
                event_type=event_type,
                user=user,
                content_type=content_type,
                object_id=object_id,
                app=app,
                organization=organization,
                description=description,
                metadata=metadata or {},
                ip_address=ip_address,
                user_agent=user_agent
            )

            logger.info(f"Audit log created: {audit_log}")
            return audit_log

        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            return None

    @staticmethod
    def _get_client_ip(request):
        """Получение IP адреса клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    # ===== УНИВЕРСАЛЬНЫЕ МЕТОДЫ =====

    @staticmethod
    def log_create(instance, user, request=None, **kwargs):
        """Логирование создания объекта"""
        return AuditLogger.log_event(
            event_type=AuditEventType.CREATE,
            content_object=instance,
            user=user,
            description=f"Создание {instance._meta.verbose_name} '{str(instance)}'",
            metadata={
                'model': instance._meta.model_name,
                'app_label': instance._meta.app_label,
                'object_id': str(instance.pk),
                'data': kwargs.get('data', {})
            },
            request=request,
            **kwargs
        )

    @staticmethod
    def log_update(instance, user, changes=None, request=None, **kwargs):
        """Логирование обновления объекта"""
        return AuditLogger.log_event(
            event_type=AuditEventType.UPDATE,
            content_object=instance,
            user=user,
            description=f"Обновление {instance._meta.verbose_name} '{str(instance)}'",
            metadata={
                'model': instance._meta.model_name,
                'app_label': instance._meta.app_label,
                'object_id': str(instance.pk),
                'changes': changes or {},
                'reason': kwargs.get('reason', '')
            },
            request=request,
            **kwargs
        )

    @staticmethod
    def log_delete(instance, user, request=None, **kwargs):
        """Логирование удаления объекта"""
        return AuditLogger.log_event(
            event_type=AuditEventType.DELETE,
            content_object=instance,
            user=user,
            description=f"Удаление {instance._meta.verbose_name} '{str(instance)}'",
            metadata={
                'model': instance._meta.model_name,
                'app_label': instance._meta.app_label,
                'object_id': str(instance.pk),
                'reason': kwargs.get('reason', '')
            },
            request=request,
            **kwargs
        )

    # ===== МАРКЕТПЛЕЙС =====

    @staticmethod
    def log_app_installation(installation, request=None, **kwargs):
        """Логирование установки приложения"""
        return AuditLogger.log_event(
            event_type=AuditEventType.APP_INSTALLATION,
            content_object=installation,
            user=installation.user,
            app=installation.app,
            organization=installation.organization,
            description=f"Установка приложения '{installation.app.name}' в организацию '{installation.organization.name}'",
            metadata={
                'app_id': str(installation.app.id),
                'app_name': installation.app.name,
                'organization_id': str(installation.organization.id),
                'organization_name': installation.organization.name,
                'installation_id': str(installation.id),
                'config': installation.config_data,
                'reason': kwargs.get('reason', '')
            },
            request=request,
            **kwargs
        )

    @staticmethod
    def log_app_uninstallation(installation, request=None, **kwargs):
        """Логирование удаления приложения"""
        return AuditLogger.log_event(
            event_type=AuditEventType.APP_UNINSTALLATION,
            content_object=installation,
            user=kwargs.get('user') or (request.user if request else None),
            app=installation.app,
            organization=installation.organization,
            description=f"Удаление приложения '{installation.app.name}' из организации '{installation.organization.name}'",
            metadata={
                'app_id': str(installation.app.id),
                'app_name': installation.app.name,
                'organization_id': str(installation.organization.id),
                'organization_name': installation.organization.name,
                'installation_id': str(installation.id),
                'reason': kwargs.get('reason', '')
            },
            request=request,
            **kwargs
        )

    @staticmethod
    def log_app_moderation(app, action, moderator, reason="", request=None, **kwargs):
        """Логирование модерации приложения"""
        return AuditLogger.log_event(
            event_type=AuditEventType.APP_MODERATION,
            content_object=app,
            user=moderator,
            app=app,
            description=f"Модерация приложения '{app.name}': {action}",
            metadata={
                'app_id': str(app.id),
                'app_name': app.name,
                'action': action,
                'old_status': kwargs.get('old_status'),
                'new_status': kwargs.get('new_status'),
                'reason': reason
            },
            request=request,
            **kwargs
        )

    # ===== ОРГАНИЗАЦИИ =====

    @staticmethod
    def log_organization_create(organization, user, request=None, **kwargs):
        """Логирование создания организации"""
        return AuditLogger.log_event(
            event_type=AuditEventType.ORGANIZATION_CREATE,
            content_object=organization,
            user=user,
            organization=organization,
            description=f"Создание организации '{organization.name}'",
            metadata={
                'organization_id': str(organization.id),
                'organization_name': organization.name,
                'inn': organization.inn,
                'created_by': str(user.id)
            },
            request=request,
            **kwargs
        )

    @staticmethod
    def log_policy_change(policy_type, changed_by, changes, request=None, **kwargs):
        """Логирование изменения политик"""
        return AuditLogger.log_event(
            event_type=AuditEventType.POLICY_CHANGE,
            user=changed_by,
            description=f"Изменение политики: {policy_type}",
            metadata={
                'policy_type': policy_type,
                'changes': changes,
                'details': kwargs.get('details', '')
            },
            request=request,
            **kwargs
        )


# Глобальный экземпляр для удобства
audit_logger = AuditLogger()
