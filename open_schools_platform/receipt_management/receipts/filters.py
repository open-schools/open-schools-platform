from django_filters import CharFilter, BooleanFilter, DateFilter, ChoiceFilter, NumberFilter

from open_schools_platform.common.filters import BaseFilterSet, UUIDInFilter, filter_by_ids, MetaCharIContainsMixin
from open_schools_platform.receipt_management.receipts.models import Receipt, ReceiptNotification


class ReceiptFilter(BaseFilterSet):
    ids = CharFilter(method=filter_by_ids)
    or_search = CharFilter(field_name="or_search", method="OR")

    payer_full_name = CharFilter(field_name="payer_full_name", lookup_expr="icontains")
    recipient_full_name = CharFilter(field_name="recipient_full_name", lookup_expr="icontains")
    student_profile = UUIDInFilter(field_name="student_profile", lookup_expr="in")

    institution_name = CharFilter(field_name="institution_name", lookup_expr="icontains")
    service_name = CharFilter(field_name="service_name", lookup_expr="icontains")
    service_category = CharFilter(field_name="service_category", lookup_expr="icontains")

    total_amount_min = NumberFilter(field_name="total_amount", lookup_expr="gte")
    total_amount_max = NumberFilter(field_name="total_amount", lookup_expr="lte")
    service_amount_min = NumberFilter(field_name="service_amount", lookup_expr="gte")
    service_amount_max = NumberFilter(field_name="service_amount", lookup_expr="lte")

    payment_due_date_from = DateFilter(field_name="payment_due_date", lookup_expr="gte")
    payment_due_date_to = DateFilter(field_name="payment_due_date", lookup_expr="lte")
    receipt_date_from = DateFilter(field_name="receipt_date", lookup_expr="gte")
    receipt_date_to = DateFilter(field_name="receipt_date", lookup_expr="lte")
    created_at_from = DateFilter(field_name="created_at", lookup_expr="gte")
    created_at_to = DateFilter(field_name="created_at", lookup_expr="lte")
    internal_receipt_number = CharFilter(field_name="internal_receipt_number", lookup_expr="icontains")

    payment_purpose = CharFilter(field_name="payment_purpose", lookup_expr="icontains")

    class Meta(MetaCharIContainsMixin):
        model = Receipt
        fields = [
            'id', 'payer_full_name', 'recipient_full_name', 'student_profile',
            'institution_name', 'service_name', 'service_category',
            'total_amount', 'service_amount', 'payment_due_date', 'receipt_date',
            'internal_receipt_number', 'payment_purpose',
            'created_at', 'updated_at'
        ]


class ReceiptNotificationFilter(BaseFilterSet):
    or_search = CharFilter(field_name="or_search", method="OR")

    receipt_recipient_name = CharFilter(field_name="receipt__recipient_full_name", lookup_expr="icontains")
    receipt_institution = CharFilter(field_name="receipt__institution_name", lookup_expr="icontains")
    receipt_service = CharFilter(field_name="receipt__service_name", lookup_expr="icontains")

    notification_type = ChoiceFilter(
        field_name="notification_type",
        choices=ReceiptNotification.NOTIFICATION_TYPES
    )
    is_delivered = BooleanFilter(field_name="is_delivered")

    created_at_from = DateFilter(field_name="created_at", lookup_expr="gte")
    created_at_to = DateFilter(field_name="created_at", lookup_expr="lte")
    sent_at_from = DateFilter(field_name="sent_at", lookup_expr="gte")
    sent_at_to = DateFilter(field_name="sent_at", lookup_expr="lte")

    class Meta(MetaCharIContainsMixin):
        model = ReceiptNotification
        fields = [
            'id', 'receipt', 'notification_type', 'is_delivered',
            'created_at', 'updated_at', 'sent_at'
        ]
