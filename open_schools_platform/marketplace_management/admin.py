from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from open_schools_platform.common.admin import admin_wrapper, BaseAdmin
from open_schools_platform.marketplace_management.models import Installation, DeveloperProfile, Category, App, \
    AppRelease, Review


@admin_wrapper(DeveloperProfile)
class DeveloperProfileModelAdmin(BaseAdmin):
    list_display = ("id", "user", "email", "github")
    field_to_highlight = "id"


@admin_wrapper(Category)
class CategoryModelAdmin(BaseAdmin):
    list_display = ("id", "name")


@admin_wrapper(App)
class AppModelAdmin(BaseAdmin):
    list_display = ("id", "name", "status", "developer_profile")


@admin_wrapper(AppRelease)
class AppReleaseModelAdmin(BaseAdmin):
    list_display = ("id", "app", "version")
    field_to_highlight = "id"


@admin_wrapper(Review)
class ReviewModelAdmin(BaseAdmin):
    list_display = ("id", "user", "app", "rating")
    field_to_highlight = "app"


class InstallationFilter(admin.SimpleListFilter):
    """Custom filter for the status"""
    title = 'Статус'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Активные'),
            ('inactive', 'Неактивные'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(active=True)
        if self.value() == 'inactive':
            return queryset.filter(active=False)
        return queryset


@admin_wrapper(Installation)
class InstallationModelAdmin(BaseAdmin):
    list_display = (
        'get_organization_name',
        'get_app_name',
        'get_installed_at',
        'get_status_display',
        'active',
        'id'
    )

    # Default sorting (new installations first)
    ordering = ('-installed_at',)

    # Filters in the right panel
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

    # Fields for quick editing
    list_editable = ('active',)

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else 'Нет школы'

    get_organization_name.short_description = 'Школа'
    get_organization_name.admin_order_field = 'organization__name'

    def get_app_name(self, obj):
        return obj.app.name if obj.app else 'Нет приложения'

    get_app_name.short_description = 'Приложение'
    get_app_name.admin_order_field = 'app__name'

    def get_installed_at(self, obj):
        if obj.installed_at:
            local_time = timezone.localtime(obj.installed_at)
            return local_time.strftime('%d.%m.%Y %H:%M')
        return 'Нет даты'

    get_installed_at.short_description = 'Дата установки'
    get_installed_at.admin_order_field = 'installed_at'

    def get_status_display(self, obj):
        if obj.active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Активен</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Неактивен</span>'
            )

    get_status_display.short_description = 'Статус'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('organization', 'app')

    # Adding custom actions
    actions = ['activate_installations', 'deactivate_installations']

    def activate_installations(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f'{updated} установок активировано')

    activate_installations.short_description = "Активировать выбранные установки"

    def deactivate_installations(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f'{updated} установок деактивировано')

    deactivate_installations.short_description = "Деактивировать выбранные установки"

    field_to_highlight = "app"
