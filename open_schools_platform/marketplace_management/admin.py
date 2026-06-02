from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from typing import Any, List, Tuple

from open_schools_platform.common.admin import admin_wrapper, BaseAdmin
from open_schools_platform.marketplace_management.models import (
    Installation,
    Category,
    App,
    Review,
    OAuth2AuthorizationCode,
    OAuth2Token,
)


@admin_wrapper(Category)
class CategoryModelAdmin(BaseAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin_wrapper(App)
class AppModelAdmin(BaseAdmin):
    # Добавил новые поля в список и фильтры
    list_display = ("id", "name", "status", "created_at", "updated_at")
    list_filter = ("status", "category")
    search_fields = ("name", "description")

    # Сгруппировал новые JSON-поля и OAuth-секреты в отдельный скрываемый блок fieldsets
    fieldsets = (
        (None, {
            "fields": ("name", "description", "status", "category", "icon_url", "screenshots", "manifest")
        }),
        ("OAuth2 Настройки", {
            "fields": ("client_secret", "redirect_uris", "grant_types", "response_types"),
            "classes": ("collapse",),  # Блок по дефолту будет свернут в админке
        }),
    )


@admin_wrapper(Review)
class ReviewModelAdmin(BaseAdmin):
    list_display = ("id", "user", "app", "rating")
    field_to_highlight = "app"
    list_filter = ("rating",)
    search_fields = ("user__username", "app__name", "message")


class InstallationFilter(admin.SimpleListFilter):
    """Custom filter for the status"""
    title = 'Статус'
    parameter_name = 'status'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[str, str]]:
        return [
            ('active', 'Активные'),
            ('inactive', 'Неактивные'),
        ]

    def queryset(self, request: Any, queryset: Any) -> Any:
        if self.value() == 'active':
            return queryset.filter(active=True)
        if self.value() == 'inactive':
            return queryset.filter(active=False)
        return queryset


@admin_wrapper(Installation)
class InstallationModelAdmin(BaseAdmin):
    list_display: Tuple[str, ...] = (
        'get_organization_name',
        'get_app_name',
        'get_installed_at',
        'get_status_display',
        'active',
        'id'
    )

    ordering = ('-installed_at',)

    list_filter = (
        'organization',
        'app',
        InstallationFilter,
    )

    search_fields = (
        'organization__name',
        'app__name'
    )

    list_per_page = 20
    list_editable = ('active',)

    def get_organization_name(self, obj: Installation) -> str:
        return obj.organization.name if obj.organization else 'Нет школы'

    get_organization_name.short_description = 'Школа'  # type: ignore[attr-defined]
    get_organization_name.admin_order_field = 'organization__name'  # type: ignore[attr-defined]

    def get_app_name(self, obj: Installation) -> str:
        return obj.app.name if obj.app else 'Нет приложения'

    get_app_name.short_description = 'Приложение'  # type: ignore[attr-defined]
    get_app_name.admin_order_field = 'app__name'  # type: ignore[attr-defined]

    def get_installed_at(self, obj: Installation) -> str:
        if obj.installed_at:
            local_time = timezone.localtime(obj.installed_at)
            return local_time.strftime('%d.%m.%Y %H:%M')
        return 'Нет даты'

    get_installed_at.short_description = 'Дата установки'  # type: ignore[attr-defined]
    get_installed_at.admin_order_field = 'installed_at'  # type: ignore[attr-defined]

    def get_status_display(self, obj: Installation) -> str:
        if obj.active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Активен</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Неактивен</span>'
            )

    get_status_display.short_description = 'Статус'  # type: ignore[attr-defined]

    def get_queryset(self, request: Any) -> Any:
        qs = super().get_queryset(request)
        return qs.select_related('organization', 'app')

    actions = ('activate_installations', 'deactivate_installations',)

    def activate_installations(self, request: Any, queryset: Any) -> None:
        updated = queryset.update(active=True)
        self.message_user(request, f'{updated} установок активировано')

    activate_installations.short_description = "Активировать выбранные установки"  # type: ignore[attr-defined]

    def deactivate_installations(self, request: Any, queryset: Any) -> None:
        updated = queryset.update(active=False)
        self.message_user(request, f'{updated} установок деактивировано')

    deactivate_installations.short_description = "Деактивировать выбранные установки"  

    field_to_highlight = "app"


