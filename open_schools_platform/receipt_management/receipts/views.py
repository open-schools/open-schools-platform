from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
import logging  # Added

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.paginators import DefaultListPagination
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.receipt_management.receipts.selectors import (
    get_receipt, get_receipts_with_filters, get_receipts_for_family,
    get_receipt_statistics_for_family, get_notifications_for_receipt,
    get_receipt_notifications
)
from open_schools_platform.receipt_management.receipts.serializers import (
    CreateReceiptSerializer, UpdateReceiptSerializer, GetReceiptSerializer,
    GetReceiptListSerializer, GetReceiptDetailedSerializer,
    UploadReceiptPDFSerializer, SendReceiptNotificationSerializer,
    GetReceiptNotificationSerializer
)
from open_schools_platform.receipt_management.receipts.services import create_receipt, process_pdf_receipt, \
    PDFDownloadService, update_receipt, bulk_send_receipt_notifications, process_pdf_receipts_bulk
from open_schools_platform.student_management.students.selectors import get_student_profile

logger = logging.getLogger(__name__)  # Added


class ReceiptCreateApi(ApiAuthMixin, APIView):
    """
    Create a new receipt (Dispatcher Web App)
    """

    @swagger_auto_schema(
        operation_description="Create a new receipt for a student",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        request_body=CreateReceiptSerializer(),
        responses={201: GetReceiptDetailedSerializer()}
    )
    def post(self, request):
        serializer = CreateReceiptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipt = create_receipt(**serializer.validated_data)

        response_serializer = GetReceiptDetailedSerializer(receipt)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class BulkReceiptPDFUploadApi(ApiAuthMixin, APIView):
    """
    Upload and parse a PDF file containing multiple receipts (Dispatcher Web App)
    """
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Upload a single PDF file containing multiple receipts. The system will attempt to parse each receipt, identify the student, and create corresponding receipt records.",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        request_body=UploadReceiptPDFSerializer,
        responses={
            200: convert_dict_to_serializer({
                "created_count": serializers.IntegerField(),
                "failed_count": serializers.IntegerField(),
                "created_receipts": GetReceiptDetailedSerializer(many=True),
                "failed_details": serializers.ListField(child=serializers.DictField())
            }),
            400: "Invalid PDF file or processing error"
        }
    )
    def post(self, request):
        serializer = UploadReceiptPDFSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pdf_file = request.FILES.get('pdf_file')
        student_profile_id = serializer.validated_data['student_profile_id']

        if not pdf_file:
            return Response({"detail": "No PDF file provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not pdf_file.name.endswith('.pdf'):
            return Response({"detail": "File must be a PDF."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = process_pdf_receipts_bulk(pdf_file, student_profile_id)

            serialized_receipts = GetReceiptDetailedSerializer(result["created_receipts"], many=True).data

            response_data = {
                "created_count": result["created_count"],
                "failed_count": result["failed_count"],
                "created_receipts": serialized_receipts,
                "failed_details": result["failed_details"]
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing bulk PDF upload: {str(e)}")
            return Response({"detail": "An error occurred while processing the PDF."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiptDetailApi(ApiAuthMixin, APIView):
    """
    Get, update, or delete a specific receipt
    """

    @swagger_auto_schema(
        operation_description="Get receipt details",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        responses={200: GetReceiptDetailedSerializer()}
    )
    def get(self, request, receipt_id):
        receipt = get_receipt(filters={'id': receipt_id}, empty_exception=True)

        # todo: Нужная сюда какая-то проверка на семью-родителя-ребенка-тд?

        serializer = GetReceiptDetailedSerializer(receipt)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update receipt details",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        request_body=UpdateReceiptSerializer(),
        responses={200: GetReceiptDetailedSerializer()}
    )
    def patch(self, request, receipt_id):
        receipt = get_receipt(filters={'id': receipt_id}, empty_exception=True)

        serializer = UpdateReceiptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_receipt = update_receipt(receipt, **serializer.validated_data)

        response_serializer = GetReceiptDetailedSerializer(updated_receipt)
        return Response(response_serializer.data)

    @swagger_auto_schema(
        operation_description="Delete a receipt",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        responses={204: "Receipt deleted successfully"}
    )
    def delete(self, request, receipt_id):
        receipt = get_receipt(filters={'id': receipt_id}, empty_exception=True)
        receipt.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReceiptListApi(ApiAuthMixin, ListAPIView):
    """
    List receipts with filtering (for both parents and dispatchers)
    """

    pagination_class = DefaultListPagination

    @swagger_auto_schema(
        operation_description="Get list of receipts",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        responses={200: GetReceiptListSerializer(many=True)}
    )
    def get(self, request):
        pagination_params = ['page', 'page_size', 'limit', 'offset']
        filters = {key: value for key, value in request.GET.dict().items()
                   if key not in pagination_params}

        # todo: Тоже здесь проверку прав накинуть

        receipts = get_receipts_with_filters(user=request.user, filters=filters)

        response = get_paginated_response(
            pagination_class=self.pagination_class,
            serializer_class=GetReceiptListSerializer,
            queryset=receipts,
            request=request,
            view=self
        )
        return response


class FamilyReceiptListApi(ApiAuthMixin, APIView):
    """
    Get receipts for a specific family (Parent Mobile App)
    """

    @swagger_auto_schema(
        operation_description="Get receipts for a family",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        responses={200: convert_dict_to_serializer({
            "results": GetReceiptListSerializer(many=True)
        })}
    )
    def get(self, request, family_id):
        family = get_family(filters={'id': family_id}, empty_exception=True)

        receipts = get_receipts_for_family(family, request.GET.dict())
        serializer = GetReceiptListSerializer(receipts, many=True)
        return Response({"results": serializer.data})


class ReceiptPDFDownloadApi(ApiAuthMixin, APIView):
    """
    Download receipt PDF (Parent Mobile App)
    Can download a single receipt or a consolidated PDF for all receipts in a family.
    """

    @swagger_auto_schema(
        operation_description="Download receipt PDF file. \n\n"
                              "If 'receipt_id' is provided, downloads a single receipt PDF.\n"
                              "If 'family_id' is provided, downloads a consolidated PDF of all receipts for that family.",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        responses={200: "PDF file"})
    def get(self, request, receipt_id=None, family_id=None):
        pdf_service = PDFDownloadService()

        if receipt_id:
            receipt = get_receipt(filters={'id': receipt_id}, user=request.user, empty_exception=True)
            return pdf_service.download_single_receipt_pdf(receipt)

        elif family_id:
            family = get_family(filters={'id': family_id}, user=request.user, empty_exception=True)
            return pdf_service.download_consolidated_family_pdf(family, request.GET.dict())

        else:
            return Response({"detail": "Either receipt_id or family_id must be provided."},
                            status=status.HTTP_400_BAD_REQUEST)


class ReceiptPDFUploadApi(ApiAuthMixin, APIView):
    """
    Upload and parse PDF receipt (Dispatcher Web App)
    """
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Upload PDF receipt file and create receipt",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        request_body=UploadReceiptPDFSerializer(),
        responses={201: GetReceiptDetailedSerializer()}
    )
    def post(self, request):
        serializer = UploadReceiptPDFSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pdf_file = serializer.validated_data['pdf_file']
        student_profile_id = serializer.validated_data['student_profile_id']

        student_profile = get_student_profile(
            filters={'id': student_profile_id},
            empty_exception=True
        )

        receipt = process_pdf_receipt(pdf_file, student_profile)

        response_serializer = GetReceiptDetailedSerializer(receipt)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReceiptNotificationSendApi(ApiAuthMixin, APIView):
    """
    Send receipt notifications (Dispatcher Web App)
    """

    @swagger_auto_schema(
        operation_description="Send notifications for receipts",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        request_body=SendReceiptNotificationSerializer(),
        responses={200: convert_dict_to_serializer({
            "sent_count": serializers.IntegerField(),
            "failed_count": serializers.IntegerField()
        })}
    )
    def post(self, request):
        serializer = SendReceiptNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipt_ids = serializer.validated_data['receipt_ids']
        notification_type = serializer.validated_data['notification_type']
        custom_message = serializer.validated_data.get('custom_message', '')

        results = bulk_send_receipt_notifications(
            receipt_ids, notification_type, custom_message
        )

        return Response({"results": results})


class ReceiptNotificationListApi(ApiAuthMixin, APIView):
    """
    List receipt notifications (Dispatcher Web App)
    """

    @swagger_auto_schema(
        operation_description="Get list of receipt notifications",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        responses={200: convert_dict_to_serializer({
            "results": GetReceiptNotificationSerializer(many=True)
        })}
    )
    def get(self, request, receipt_id=None):
        if receipt_id:
            receipt = get_receipt(filters={'id': receipt_id}, empty_exception=True)
            notifications = get_notifications_for_receipt(receipt)
        else:
            filters = request.GET.dict()
            notifications = get_receipt_notifications(filters=filters)

        serializer = GetReceiptNotificationSerializer(notifications, many=True)
        return Response({"results": serializer.data})


class FamilyReceiptStatisticsApi(ApiAuthMixin, APIView):
    """
    Get receipt statistics for a family (Parent Mobile App)
    """

    @swagger_auto_schema(
        operation_description="Get receipt statistics for a family",
        tags=[SwaggerTags.RECEIPT_MANAGEMENT_RECEIPTS],
        responses={200: convert_dict_to_serializer({
            "total_receipts": serializers.IntegerField(),
            "overdue_receipts": serializers.IntegerField(),
            "viewed_receipts": serializers.IntegerField(),
            "total_amount": serializers.DecimalField(max_digits=10, decimal_places=2)
        })}
    )
    def get(self, request, family_id):
        family = get_family(filters={'id': family_id}, empty_exception=True)

        if hasattr(request.user, 'parent_profile'):
            if family not in request.user.parent_profile.families.all():
                raise Http404("Family not found")

        statistics = get_receipt_statistics_for_family(family)
        return Response({"statistics": statistics})
