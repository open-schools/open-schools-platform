from django.contrib import admin

from open_schools_platform.parent_management.families.models import Family


class FamilyAdmin(admin.ModelAdmin):
    list_display = ("name", "id")
    search_fields = ("name",)


admin.site.register(Family, FamilyAdmin)
