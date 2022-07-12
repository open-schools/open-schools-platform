from django.contrib import admin
from .models import Circle


# Register your models here.


class CircleAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


admin.site.register(Circle, CircleAdmin)
