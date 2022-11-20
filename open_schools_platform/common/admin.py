from typing import Type, Sequence, Union, Callable, Any, Tuple

from django.contrib import admin, messages
from django.contrib.admin import register
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.utils.encoding import force_str
from safedelete import HARD_DELETE, SOFT_DELETE, SOFT_DELETE_CASCADE, NO_DELETE
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter

from open_schools_platform.common.models import BaseModel


class BaseAdmin(SafeDeleteAdmin):
    list_display = ("highlight_deleted_field",)  # type: Sequence[Union[str, Callable[[Any], Any]]]
    list_filter = (SafeDeleteAdminFilter,) + SafeDeleteAdmin.list_filter  # type: ignore[operator]
    actions: Tuple = ()
    field_to_highlight = "name"

    @admin.action(description='Hard deleted selected')
    def hard_delete_selected(self, request, queryset):
        """ Admin action to hard delete objects in bulk with confirmation. """
        if not self.has_delete_permission(request):
            raise PermissionDenied
        assert hasattr(queryset, 'delete')

        requested = queryset.count()
        changed = 0
        if requested:
            for obj in queryset:
                obj_display = force_str(obj)
                self.log_deletion(request, obj, obj_display)
            df = queryset.delete(force_policy=HARD_DELETE)
            changed += df[1]['users.User']
            if changed < requested:
                self.message_user(
                    request,
                    "Successfully deleted %(count_changed)d of the "
                    "%(count_requested)d selected %(items)s." % {
                        "count_requested": requested,
                        "count_changed": changed,
                        "items": model_ngettext(self.opts, requested)
                    },
                    messages.WARNING,
                )
            else:
                self.message_user(
                    request,
                    "Successfully deleted %(count)d %(items)s." % {
                        "count": requested,
                        "items": model_ngettext(self.opts, requested)
                    },
                    messages.SUCCESS,
                )
            return None

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


def hard_delete_queryset(self, request, queryset):
    queryset.delete(force_policy=HARD_DELETE)


def admin_wrapper(model: Type[BaseModel]):
    def wrap_admin_model(admin_model: Type[BaseAdmin]):
        delete_policy = model._safedelete_policy
        if delete_policy:
            if delete_policy == SOFT_DELETE or delete_policy == SOFT_DELETE_CASCADE:
                admin_model.actions = ('hard_delete_selected', 'undelete_selected')
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
