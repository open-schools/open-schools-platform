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


@admin_wrapper(Installation)
class InstallationModelAdmin(BaseAdmin):
    list_display = ("id", "app", "active")
    field_to_highlight = "app"
