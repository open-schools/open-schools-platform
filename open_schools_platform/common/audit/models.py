# common/audit/models.py
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from safedelete.models import SafeDeleteModel


class AuditEventType(models.TextChoices):
    """Типы событий аудита"""
    CREATE = 'create', 'Создание'
    UPDATE = 'update', 'Обновление'
    DELETE = 'delete', 'Удаление'

    # Маркетплейс
    APP_INSTALLATION = 'app_installation', 'Установка приложения'
    APP_UNINSTALLATION = 'app_uninstallation', 'Удаление приложения'
    APP_MODERATION = 'app_moderation', 'Модерация'
    POLICY_CHANGE = 'policy_change', 'Изменение политик'
    APP_UPDATE = 'app_update', 'Обновление приложения'

    # Организации
    ORGANIZATION_CREATE = 'organization_create', 'Создание организации'
    ORGANIZATION_UPDATE = 'organization_update', 'Обновление организации'

    # Круги
    CIRCLE_CREATE = 'circle_create', 'Создание кружка'
    CIRCLE_UPDATE = 'circle_update', 'Обновление кружка'

    # Пользователи
    USER_LOGIN = 'user_login', 'Вход пользователя'
    USER_LOGOUT = 'user_logout', 'Выход пользователя'

    # Общие
    SYSTEM_EVENT = 'system_event', 'Системное событие'


class AuditLog(SafeDeleteModel):
    """Универсальная модель для логирования действий"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Тип события
    event_type = models.CharField(
        max_length=50,
        choices=AuditEventType.choices,
        verbose_name='Тип события'
    )

    # Кто совершил действие
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Пользователь',
        related_name='audit_logs'
    )

    # Универсальная ссылка на любой объект
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Тип объекта'
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='ID объекта'
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # Прямые ссылки для удобства фильтрации
    app = models.ForeignKey(
        'marketplace_management.App',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Приложение',
        related_name='audit_logs'
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Организация',
        related_name='audit_logs'
    )

    # Описание
    description = models.TextField(verbose_name='Описание события')

    # Метаданные
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Метаданные'
    )

    # Контекст
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP адрес'
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='User Agent'
    )

    # Временные метки
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Лог аудита'
        verbose_name_plural = 'Логи аудита'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['app']),
            models.Index(fields=['organization']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def get_object_url(self):
        """Получить URL объекта в админке"""
        if self.content_type and self.object_id:
            try:
                from django.urls import reverse
                model_name = self.content_type.model
                app_label = self.content_type.app_label
                return reverse(f'admin:{app_label}_{model_name}_change', args=[self.object_id])
            except:
                return None
        return None
