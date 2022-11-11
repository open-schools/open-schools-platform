from django.contrib import admin
from typing import Any, Sequence, Union, Callable, Type

from django.contrib.admin import SimpleListFilter

text_type = str


def highlight_deleted(obj): ...


class SafeDeleteAdminFilter(admin.SimpleListFilter):
    title: Any
    parameter_name: Any

    def lookups(self, request, model_admin): ...

    def queryset(self, request, queryset): ...


class SafeDeleteAdmin(admin.ModelAdmin):
    undelete_selected_confirmation_template: str
    list_display: Sequence[Union[str, Callable[[Any], Any]]]
    list_filter: Sequence[Union[str, Type[SimpleListFilter]]]
    actions: Any

    class Meta:
        abstract: bool

    class Media:
        css: Any

    def queryset(self, request): ...

    def get_queryset(self, request): ...

    def log_undeletion(self, request, obj, object_repr) -> None: ...

    def undelete_selected(self, request, queryset): ...

    def highlight_deleted_field(self, obj): ...

    field_to_highlight: Any
