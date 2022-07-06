from django.contrib import admin

from open_schools_platform.parent_management.families.models import Family


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
