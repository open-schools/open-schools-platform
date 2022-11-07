from typing import Type, Sequence, Union, Callable, Any

from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter


class BaseAdmin(SafeDeleteAdmin):
    list_display = ("highlight_deleted_field",)  # type: Sequence[Union[str, Callable[[Any], Any]]]
    list_filter = (SafeDeleteAdminFilter,) + SafeDeleteAdmin.list_filter  # type: ignore[operator]
    field_to_highlight = "name"

    class Meta:
        abstract = True


class InputFilter(admin.SimpleListFilter):
    template = 'templates/input_filter.html'

    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


def admin_wrapper(admin_model: Type[BaseAdmin]):
    admin_model.highlight_deleted_field.short_description = admin_model.field_to_highlight  # type: ignore[attr-defined]

    if admin_model.list_display:
        admin_model.list_display = BaseAdmin.list_display + admin_model.list_display  # type: ignore[operator]
    else:
        admin_model.list_display = BaseAdmin.list_display

    if admin_model.list_filter:
        admin_model.list_filter = BaseAdmin.list_filter + admin_model.list_filter
    else:
        admin_model.list_filter = BaseAdmin.list_filter

    return admin_model
