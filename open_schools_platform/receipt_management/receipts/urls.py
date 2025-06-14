from django.urls import path

from open_schools_platform.common.views import MultipleViewManager
from open_schools_platform.receipt_management.receipts.views import (
    ReceiptCreateApi, ReceiptDetailApi, ReceiptListApi, FamilyReceiptListApi,
    ReceiptPDFDownloadApi, ReceiptPDFUploadApi, BulkReceiptPDFUploadApi,
    ReceiptNotificationSendApi, FamilyReceiptStatisticsApi
)

urlpatterns = [
    path('', MultipleViewManager({'get': ReceiptListApi, 'post': ReceiptCreateApi}).as_view(),
         name='receipts-list-create'),
    path('/<uuid:receipt_id>', ReceiptDetailApi.as_view(), name='receipt-detail'),

    path('/family/<uuid:family_id>', FamilyReceiptListApi.as_view(), name='family-receipts'),
    path('/family/<uuid:family_id>/statistics', FamilyReceiptStatisticsApi.as_view(), name='family-receipt-statistics'),
    path('/family/<uuid:family_id>/download', ReceiptPDFDownloadApi.as_view(), name='family-receipts-pdf-download'),

    path('/<uuid:receipt_id>/download', ReceiptPDFDownloadApi.as_view(), name='receipt-pdf-download'),

    path('/upload-pdf', ReceiptPDFUploadApi.as_view(), name='receipt-pdf-upload'),
    path('/upload-bulk-pdf', BulkReceiptPDFUploadApi.as_view(), name='receipt-bulk-pdf-upload'),

    path('/send-notifications', ReceiptNotificationSendApi.as_view(), name='receipt-send-notifications'),
]
