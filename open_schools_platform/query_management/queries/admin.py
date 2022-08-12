from django.contrib import admin
from open_schools_platform.common.admin import InputFilter
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_query, get_queries
from open_schools_platform.query_management.queries.services import run_sender_handler
from django.utils.translation import gettext_lazy as _


class SenderCTFilter(InputFilter):
    parameter_name = 'sender_ct_model'
    title = _('sender CT model')

    def queryset(self, request, queryset):
        if self.value() is not None:
            sender = self.value()

            return get_queries(filters={"sender_ct_search": sender})


class RecipientCTFilter(InputFilter):
    parameter_name = 'recipient_ct_model'
    title = _('recipient CT model')

    def queryset(self, request, queryset):
        if self.value() is not None:
            recipient = self.value()

            return get_queries(filters={"recipient_ct_search": recipient})


class SenderUUIDFilter(InputFilter):
    parameter_name = 'sender_uuid'
    title = _('sender UUID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            sender_uuid = self.value()

            return get_queries(filters={'sender_id': sender_uuid})


class RecipientUUIDFilter(InputFilter):
    parameter_name = 'recipient_uuid'
    title = _('recipient UUID')

    def queryset(self, request, queryset):
        if self.value() is not None:
            recipient_uuid = self.value()

            return get_queries(filters={'recipient_id': recipient_uuid})


class QueryAdmin(admin.ModelAdmin):
    list_display = ("id", "sender_ct", "recipient_ct", "status", "created_at")
    list_filter = ("status", SenderCTFilter, SenderUUIDFilter, RecipientCTFilter, RecipientUUIDFilter)

    def save_model(self, request, obj, form, change):
        old_query = get_query(filters={"id": str(obj.id)})
        if "status" in form.changed_data:
            run_sender_handler(query=old_query, new_status=obj.status, user=request.user)
        return super().save_model(request, obj, form, change)


admin.site.register(Query, QueryAdmin)
