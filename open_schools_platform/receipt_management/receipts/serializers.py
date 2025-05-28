from django.utils import timezone
from rest_framework import serializers

from open_schools_platform.common.serializers import BaseModelSerializer
from open_schools_platform.receipt_management.receipts.models import Receipt, ReceiptNotification, ReceiptService
from open_schools_platform.student_management.students.serializers import GetStudentProfileSerializer


class ReceiptServiceSerializer(BaseModelSerializer):
    """Serializer for individual receipt services"""

    class Meta:
        model = ReceiptService
        fields = [
            'id', 'institution', 'service_name', 'debt_at_month_start',
            'charged_this_month', 'recalculation_amount', 'paid_amount',
            'debt_at_next_month_start', 'prepayment', 'service_amount'
        ]


class CreateReceiptSerializer(BaseModelSerializer):
    """Serializer for creating receipts - used by dispatchers"""

    class Meta:
        model = Receipt
        fields = [
            'student_profile', 'internal_receipt_number', 'payer_full_name',
            'recipient_full_name', 'institution_name', 'service_name',
            'service_category', 'debt_at_month_start', 'charged_this_month', 'recalculation_amount',
            'paid_amount', 'debt_at_next_month_start', 'prepayment',
            'service_amount', 'total_amount', 'receipt_date', 'payment_due_date',
            'payment_purpose', 'qr_code_data', 'pdf_file'
        ]


class UpdateReceiptSerializer(serializers.Serializer):
    """Serializer for updating receipts"""

    internal_receipt_number = serializers.CharField(max_length=100, required=False)
    payer_full_name = serializers.CharField(max_length=300, required=False)
    recipient_full_name = serializers.CharField(max_length=300, required=False)
    institution_name = serializers.CharField(max_length=500, required=False)
    service_name = serializers.CharField(max_length=300, required=False)
    service_category = serializers.CharField(max_length=200, required=False, allow_blank=True)
    debt_at_month_start = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    charged_this_month = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    recalculation_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    debt_at_next_month_start = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    prepayment = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    service_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    receipt_date = serializers.DateField(required=False)
    payment_due_date = serializers.DateField(required=False)
    payment_purpose = serializers.CharField(required=False)
    qr_code_data = serializers.CharField(required=False, allow_blank=True)
    pdf_file = serializers.FileField(required=False)


class GetReceiptSerializer(BaseModelSerializer):
    """Serializer for getting receipt details - used by parents mobile app"""

    student_profile = GetStudentProfileSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    services = ReceiptServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Receipt
        fields = [
            'id', 'student_profile', 'internal_receipt_number', 'payer_full_name', 'recipient_full_name',
            'institution_name', 'service_name',
            'service_category', 'service_amount', 'total_amount', 'receipt_date',
            'payment_due_date', 'payment_purpose', 'qr_code_data',
            'is_overdue', 'pdf_file', 'services', 'created_at'
        ]


class GetReceiptListSerializer(BaseModelSerializer):
    """Serializer for receipt list - simplified view for mobile app"""

    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Receipt
        fields = [
            'id', 'recipient_full_name', 'payer_full_name', 'institution_name', 'service_name',
            'total_amount', 'receipt_date', 'payment_due_date',
            'is_overdue', 'created_at'
        ]


class GetReceiptDetailedSerializer(BaseModelSerializer):
    """Serializer for detailed receipt view - used by dispatchers"""

    student_profile = GetStudentProfileSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    notifications_count = serializers.SerializerMethodField()
    services = ReceiptServiceSerializer(many=True, read_only=True)

    def get_notifications_count(self, obj):
        return obj.notifications.count()

    class Meta:
        model = Receipt
        fields = [
            'id', 'student_profile', 'internal_receipt_number', 'payer_full_name',
            'recipient_full_name', 'institution_name', 'service_name', 'service_category', 'debt_at_month_start',
            'charged_this_month', 'recalculation_amount',
            'paid_amount', 'debt_at_next_month_start', 'prepayment',
            'service_amount', 'total_amount', 'receipt_date', 'payment_due_date',
            'payment_purpose', 'qr_code_data',
            'is_overdue', 'pdf_file', 'notifications_count', 'services', 'created_at']


class UploadReceiptPDFSerializer(serializers.Serializer):
    """Serializer for PDF file upload and parsing"""

    pdf_file = serializers.FileField()
    student_profile_id = serializers.UUIDField(required=False)

    def validate_pdf_file(self, value):
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("File must be a PDF")

        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 10MB")

        return value


class BulkReceiptUploadSerializer(serializers.Serializer):
    """Serializer for bulk receipt upload"""

    pdf_files = serializers.ListField(
        child=serializers.FileField(),
        min_length=1,
        max_length=50
    )

    def validate_pdf_files(self, value):
        for file in value:
            if not file.name.endswith('.pdf'):
                raise serializers.ValidationError(f"File {file.name} must be a PDF")

            if file.size > 10 * 1024 * 1024:
                raise serializers.ValidationError(f"File {file.name} size must be less than 10MB")

        return value


class SendReceiptNotificationSerializer(serializers.Serializer):
    """Serializer for sending receipt notifications"""

    receipt_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    notification_type = serializers.ChoiceField(
        choices=ReceiptNotification.NOTIFICATION_TYPES,
        default='initial'
    )
    custom_message = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Custom message to include in notification"
    )


class GetReceiptNotificationSerializer(BaseModelSerializer):
    """Serializer for receipt notifications"""

    receipt_id = serializers.UUIDField(source='receipt.id')
    receipt_number = serializers.CharField(source='receipt.internal_receipt_number')

    class Meta:
        model = ReceiptNotification
        fields = [
            'id', 'receipt_id', 'receipt_number', 'notification_type',
            'sent_at', 'is_delivered'
        ]
