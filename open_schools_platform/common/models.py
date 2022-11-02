import safedelete
from django.db import models
from django.utils import timezone
from rules.contrib.models import RulesModelMixin, RulesModelBase
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter
from safedelete.models import SafeDeleteModel


class BaseModel(RulesModelMixin, SafeDeleteModel, metaclass=RulesModelBase):
    _safedelete_policy = safedelete.config.NO_DELETE
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DeleteAdmin(SafeDeleteAdmin):
    list_display = ("highlight_deleted_field",)
    list_filter = (SafeDeleteAdminFilter,) + SafeDeleteAdmin.list_filter
    field_to_highlight = "name"

    @staticmethod
    def init_model(unit_admin):
        unit_admin.highlight_deleted_field.short_description = unit_admin.field_to_highlight

    class Meta:
        abstract = True
