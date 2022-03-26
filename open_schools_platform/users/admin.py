from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from open_schools_platform.users.models import User, CreationToken
from open_schools_platform.users.services import create_user


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'is_admin', 'name', 'is_superuser', 'is_active', 'created_at', 'updated_at')

    search_fields = ('phone', 'name')

    list_filter = ('is_active', 'is_admin')

    fieldsets = (
        (
            None, {
                'fields': ("phone", "name")
            }
        ),
        (
            "Booleans", {
                "fields": ("is_active", "is_admin")
            }
        ),
        (
            "Timestamps", {
                "fields": ("created_at", "updated_at")
            }
        )
    )

    readonly_fields = ("created_at", "updated_at", )

    def save_model(self, request, obj, form, change):
        if change:
            return super().save_model(request, obj, form, change)
        try:
            create_user(**form.cleaned_data)
        except ValidationError as exc:
            self.message_user(request, str(exc), messages.ERROR)


admin.site.register(CreationToken)
