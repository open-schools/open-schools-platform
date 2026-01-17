from typing import Any, List, Tuple
from django.contrib import admin
from django.http import HttpRequest
from django.utils import timezone
from django.utils.html import format_html

from open_schools_platform.common.admin import admin_wrapper, BaseAdmin
from open_schools_platform.marketplace_management.models import (
    DeveloperProfile,
    Category,
    App,
    AppRelease,
    Review,
    Installation,
    InstallationStatusLog,
    InstallationStatus,
)
from open_schools_platform.marketplace_management.services.installation_status import (
    InstallationStatusService,
)


@admin_wrapper(DeveloperProfile)
class DeveloperProfileModelAdmin(BaseAdmin):
    list_display: Tuple[str, ...] = ("id", "user", "email", "github")
    field_to_highlight: str = "id"


@admin_wrapper(Category)
class CategoryModelAdmin(BaseAdmin):
    list_display: Tuple[str, ...] = ("id", "name")


@admin_wrapper(App)
class AppModelAdmin(BaseAdmin):
    list_display: Tuple[str, ...] = ("id", "name", "status", "developer_profile")


@admin_wrapper(AppRelease)
class AppReleaseModelAdmin(BaseAdmin):
    list_display: Tuple[str, ...] = ("id", "app", "version")
    field_to_highlight: str = "id"


@admin_wrapper(Review)
class ReviewModelAdmin(BaseAdmin):
    list_display: Tuple[str, ...] = ("id", "user", "app", "rating", "created_at")
    field_to_highlight: str = "app"


class InstallationStatusLogInline(admin.TabularInline):
    model = InstallationStatusLog
    extra: int = 0
    can_delete: bool = False
    show_change_link: bool = False

    readonly_fields: Tuple[str, ...] = (
        "old_status",
        "new_status",
        "changed_by",
        "changed_at",
    )

    fields: Tuple[str, ...] = readonly_fields
    ordering = ("-changed_at",)

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

class InstallationFilter(admin.SimpleListFilter):
    """Custom filter for the status"""

    title = "Статус"
    parameter_name = "status"


class InstallationStatusFilter(admin.SimpleListFilter):
    title: str = "Статус"
    parameter_name: str = "status"

    def lookups(
        self,
        request: HttpRequest,
        model_admin: admin.ModelAdmin,
    ) -> List[Tuple[Any, str]]:
        return InstallationStatus.choices

    def queryset(self, request: HttpRequest, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


@admin_wrapper(Installation)
class InstallationModelAdmin(BaseAdmin):
    list_display: Tuple[str, ...] = (
        "get_organization_name",
        "get_app_name",
        "get_installed_at",
        "get_status_display",
        "status",
        "active",
        "id",
    )

    ordering: Tuple[str, ...] = ("-installed_at",)

    list_filter: Tuple[Any, ...] = (
        "organization",
        "app",
        InstallationStatusFilter,
    )

    search_fields: Tuple[str, ...] = (
        "organization__name",
        "app__name",
    )

    list_per_page: int = 20

    readonly_fields: Tuple[str, ...] = (
        "active",
        "installed_at",
        "disabled_at",
        "re_activated_at",
        "uninstalled_at",
    )

    field_to_highlight: str = "app"

    inlines = (InstallationStatusLogInline,)

    fields: Tuple[str, ...] = (
        "organization",
        "app",
        "user",
        "status",
        "active",
        "installed_at",
        "disabled_at",
        "re_activated_at",
        "uninstalled_at",
        "config_data",
    )

    @admin.display(description="Школа", ordering="organization__name")
    def get_organization_name(self, obj: Installation) -> str:
        return obj.organization.name if obj.organization else "Нет школы"

    get_organization_name.short_description = "Школа"  # type: ignore[attr-defined]
    get_organization_name.admin_order_field = "organization__name"  # type: ignore[attr-defined]

    @admin.display(description="Приложение", ordering="app__name")
    def get_app_name(self, obj: Installation) -> str:
        return obj.app.name if obj.app else "Нет приложения"

    get_app_name.short_description = "Приложение"  # type: ignore[attr-defined]
    get_app_name.admin_order_field = "app__name"  # type: ignore[attr-defined]

    @admin.display(description="Дата установки", ordering="installed_at")
    def get_installed_at(self, obj: Installation) -> str:
        if not obj.installed_at:
            return "Нет даты"
        local_time = timezone.localtime(obj.installed_at)
        return local_time.strftime("%d.%m.%Y %H:%M")

    @admin.display(description="Статус")
    def get_status_display(self, obj: Installation) -> str:
        color_map: dict[str, str] = {
            InstallationStatus.STATUS_ACTIVE: "green",
            InstallationStatus.STATUS_DISABLED: "orange",
            InstallationStatus.STATUS_UNINSTALLED: "red",
        }
        label_map: dict[str, str] = {
            InstallationStatus.STATUS_ACTIVE: "Активен",
            InstallationStatus.STATUS_DISABLED: "Отключён",
            InstallationStatus.STATUS_UNINSTALLED: "Удалён",
        }

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color_map.get(obj.status, "gray"),
            label_map.get(obj.status, obj.status),
        )

    def get_queryset(self, request: HttpRequest):
        return (
            super()
            .get_queryset(request)
            .select_related("organization", "app")
        )

    def save_model(
        self,
        request: HttpRequest,
        obj: Installation,
        form,
        change: bool,
    ) -> None:
        if not change:
            super().save_model(request, obj, form, change)
            return

        old_status: str = Installation.objects.get(pk=obj.pk).status
        new_status: str = form.cleaned_data.get("status")

        if old_status != new_status:
            # rollback in-memory value
            obj.status = old_status

            InstallationStatusService.change_status(
                installation=obj,
                new_status=new_status,
                user=request.user,
            )
        else:
            super().save_model(request, obj, form, change)

    get_status_display.short_description = 'Статус'  # type: ignore[attr-defined]

    def get_queryset(self, request: Any) -> Any:
        qs = super().get_queryset(request)
        return qs.select_related('organization', 'app')

    field_to_highlight = "app"
