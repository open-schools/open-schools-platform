# common/audit/admin.py
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from .models import AuditLog, AuditEventType


class EventTypeFilter(admin.SimpleListFilter):
    title = 'Тип события'
    parameter_name = 'event_type'

    def lookups(self, request, model_admin):
        return AuditEventType.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(event_type=self.value())
        return queryset


class ContentTypeFilter(admin.SimpleListFilter):
    title = 'Тип объекта'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        content_type_ids = AuditLog.objects.values_list('content_type', flat=True).distinct()
        content_types = ContentType.objects.filter(id__in=content_type_ids)
        return [(ct.id, ct.model_class()._meta.verbose_name if ct.model_class() else ct.model)
                for ct in content_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=self.value())
        return queryset


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'created_at',
        'event_type_display',
        'user_link',
        'content_object_link',
        'app_link',
        'organization_link',
        'ip_address',
        'short_description'
    ]

    list_filter = [
        EventTypeFilter,
        ContentTypeFilter,
        'created_at',
        'user',
        'app',
        'organization',
        'ip_address'
    ]

    search_fields = [
        'description',
        'user__username',
        'user__email',
        'app__name',
        'organization__name',
        'metadata',
        'object_id',
        'ip_address'
    ]

    readonly_fields = [
        'id',
        'event_type',
        'user',
        'content_type',
        'object_id',
        'content_object_link',
        'app',
        'organization',
        'description',
        'metadata',
        'ip_address',
        'user_agent',
        'created_at',
        'deleted'
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('event_type', 'description', 'created_at')
        }),
        ('Участники', {
            'fields': ('user', 'content_object_link', 'app', 'organization')
        }),
        ('Контекст', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Техническая информация', {
            'fields': ('id', 'metadata', 'content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('deleted',),
            'classes': ('collapse',)
        }),
    )

    def event_type_display(self, obj):
        return obj.get_event_type_display()

    event_type_display.short_description = 'Тип события'

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "-"

    user_link.short_description = 'Пользователь'

    def content_object_link(self, obj):
        if obj.content_object:
            url = obj.get_object_url()
            if url:
                return format_html('<a href="{}">{}</a>', url, str(obj.content_object))
            return str(obj.content_object)
        return "-"

    content_object_link.short_description = 'Объект'

    def app_link(self, obj):
        if obj.app:
            url = reverse('admin:marketplace_management_app_change', args=[obj.app.id])
            return format_html('<a href="{}">{}</a>', url, obj.app.name)
        return "-"

    app_link.short_description = 'Приложение'

    def organization_link(self, obj):
        if obj.organization:
            url = reverse('admin:organizations_organization_change', args=[obj.organization.id])
            return format_html('<a href="{}">{}</a>', url, obj.organization.name)
        return "-"

    organization_link.short_description = 'Организация'

    def short_description(self, obj):
        if len(obj.description) > 100:
            return f"{obj.description[:100]}..."
        return obj.description

    short_description.short_description = 'Описание'

    def has_add_permission(self, request):
        return False  # Нельзя создавать логи вручную

    def has_change_permission(self, request, obj=None):
        return False  # Нельзя редактировать логи

    def has_delete_permission(self, request, obj=None):
        # Только суперпользователь может удалять логи
        return request.user.is_superuser

    def get_queryset(self, request):
        # Показываем все логи, включая удаленные для суперпользователя
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.all_with_deleted()
        return qs

    class Media:
        css = {
            'all': ('admin/css/audit_logs.css',)
        }