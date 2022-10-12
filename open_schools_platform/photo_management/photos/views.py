from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import swagger_dict_response
from open_schools_platform.photo_management.photos.selectors import get_photo
from open_schools_platform.photo_management.photos.serializers import PhotoSerializer
from open_schools_platform.photo_management.photos.services import update_photo


class PhotoApi(ApiAuthMixin, APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Create photo",
        request_body=PhotoSerializer,
        responses={201: swagger_dict_response({"photo": PhotoSerializer()}), },
        tags=[SwaggerTags.PHOTO_MANAGEMENT_PHOTOS]
    )
    def put(self, request, pk):
        photo_serializer = PhotoSerializer(data=request.data)
        photo_serializer.is_valid(raise_exception=True)

        photo = get_photo(filters={"id": str(pk)}, empty_exception=True, empty_message="photo doesn't exist")
        update_photo(photo=photo, data=photo_serializer.validated_data)

        return Response({"photo": PhotoSerializer(photo).data}, status=201)
