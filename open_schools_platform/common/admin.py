from typing import Type, Sequence, Union, Callable, Any, Tuple

from django.contrib import admin
from django.contrib.admin import register
from safedelete import HARD_DELETE, SOFT_DELETE, SOFT_DELETE_CASCADE, NO_DELETE
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter

from open_schools_platform.common.models import BaseModel


class BaseAdmin(SafeDeleteAdmin):
    list_display = ("highlight_deleted_field",)  # type: Sequence[Union[str, Callable[[Any], Any]]]
    list_filter = (SafeDeleteAdminFilter,) + SafeDeleteAdmin.list_filter  # type: ignore[operator]
    actions: Tuple = ()
    field_to_highlight = "name"

    class Meta:
        abstract = True


class InputFilter(admin.SimpleListFilter):
    """
    InputFilter allows to create custom filters for django admin.
    To use it, you need to inherit from it in a class.

    The class should contain:
    - parameter_name and title attributes.
    - redefined queryset method.

    You can look for usage examples in this project.
    """

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


def hard_delete_queryset(self, request, queryset):
    queryset.delete(force_policy=HARD_DELETE)


def admin_wrapper(model: Type[BaseModel]):
    """
    This function is used to wrap the model with the admin class.
    Configures the admin panel for soft deletion.
    """

    def wrap_admin_model(admin_model: Type[BaseAdmin]):
        delete_policy = model._safedelete_policy
        if delete_policy:
            if delete_policy == SOFT_DELETE or delete_policy == SOFT_DELETE_CASCADE:
                admin_model.actions = ('undelete_selected',)
                admin_model.highlight_deleted_field.short_description = admin_model.field_to_highlight  # type: ignore[attr-defined] # noqa

                if admin_model.list_display:
                    admin_model.list_display = BaseAdmin.list_display + admin_model.list_display  # type: ignore[operator] # noqa
                else:
                    admin_model.list_display = BaseAdmin.list_display
                if admin_model.list_filter:
                    admin_model.list_filter = BaseAdmin.list_filter + admin_model.list_filter
                else:
                    admin_model.list_filter = BaseAdmin.list_filter

            if delete_policy == NO_DELETE:
                admin_model.delete_queryset = hard_delete_queryset  # type: ignore[assignment]

        return register(model)(admin_model)

    return wrap_admin_model
