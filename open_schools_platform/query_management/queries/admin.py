from django.contrib import admin
from open_schools_platform.common.admin import InputFilter
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_query, get_queries
from open_schools_platform.query_management.queries.services import run_sender_handler
from django.utils.translation import gettext_lazy as _


class SenderFilter(InputFilter):
    parameter_name = 'sender'
    title = _('sender')

    def queryset(self, request, queryset):
        if self.value() is not None:
            sender = self.value()

            return get_queries(filters={"sender_ct_search": sender})


class RecipientFilter(InputFilter):
    parameter_name = 'recipient'
    title = _('recipient')

    def queryset(self, request, queryset):
        if self.value() is not None:
            recipient = self.value()

            return get_queries(filters={"recipient_ct_search": recipient})


class QueryAdmin(admin.ModelAdmin):
    list_display = ("id", "sender_ct", "recipient_ct", "status")
    list_filter = ("status", SenderFilter, RecipientFilter)

    def save_model(self, request, obj, form, change):
        old_query = get_query(filters={"id": str(obj.id)})
        if "status" in form.changed_data:
            run_sender_handler(query=old_query, new_status=obj.status, user=request.user)
        return super().save_model(request, obj, form, change)


admin.site.register(Query, QueryAdmin)
