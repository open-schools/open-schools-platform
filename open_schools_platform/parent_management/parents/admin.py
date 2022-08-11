from django.contrib import admin

from open_schools_platform.parent_management.parents.models import ParentProfile


class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'id')
    search_fields = ('name', 'user__phone')


admin.site.register(ParentProfile, ParentProfileAdmin)
