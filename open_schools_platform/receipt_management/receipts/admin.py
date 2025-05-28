from django.contrib import admin
from django.utils.html import format_html

from .models import Receipt, ReceiptNotification


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = [
        'internal_receipt_number', 'recipient_full_name', 'student_profile_name',
        'institution_name', 'total_amount', 'payment_due_date',
        'created_at', 'pdf_file_link'
    ]
    list_filter = [
        'payment_due_date', 'created_at', 'institution_name',
        'service_category'
    ]
    search_fields = [
        'internal_receipt_number', 'recipient_full_name', 'payer_full_name',
        'institution_name', 'service_name', 'student_profile__user__first_name',
        'student_profile__user__last_name'    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Student Information', {
            'fields': ('student_profile', 'recipient_full_name', 'payer_full_name')
        }),
        ('Receipt Details', {
            'fields': ('internal_receipt_number', 'institution_name', 'service_name',
                       'service_category', 'payment_purpose')
        }),
        ('Financial Information', {
            'fields': ('debt_at_month_start', 'recalculation_amount', 'paid_amount',
                       'debt_at_next_month_start', 'prepayment', 'service_amount', 'total_amount')
        }),
        ('Dates', {
            'fields': ('receipt_date', 'payment_due_date')
        }),
        ('Files & QR Codes', {
            'fields': ('pdf_file', 'qr_code_data')        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def student_profile_name(self, obj):
        """Display student name from profile"""
        if obj.student_profile:
            return f"{obj.student_profile.user.first_name} {obj.student_profile.user.last_name}"
        return "N/A"

    student_profile_name.short_description = "Student Name"

    def pdf_file_link(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">Download PDF</a>',
                obj.pdf_file.url
            )
        return "No PDF"

    pdf_file_link.short_description = "PDF File"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student_profile__user')


@admin.register(ReceiptNotification)
class ReceiptNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'receipt_number', 'notification_type',
        'is_delivered', 'sent_at', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_delivered', 'sent_at', 'created_at'
    ]
    search_fields = [
        'receipt__internal_receipt_number', 'receipt__recipient_full_name',
        'receipt__payer_full_name', 'receipt__institution_name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'sent_at']

    fieldsets = (
        ('Notification Details', {
            'fields': ('receipt', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_delivered', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def receipt_number(self, obj):
        """Display receipt number"""
        return obj.receipt.internal_receipt_number if obj.receipt else "N/A"

    receipt_number.short_description = "Receipt Number"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('receipt')
