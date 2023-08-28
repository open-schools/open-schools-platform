from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.views import convert_dict_to_serializer
from open_schools_platform.photo_management.photos.selectors import get_photo
from open_schools_platform.photo_management.photos.serializers import GetPhotoSerializer, UpdatePhotoSerializer
from open_schools_platform.photo_management.photos.services import update_photo


class PhotoApi(ApiAuthMixin, APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Update photo",
        request_body=UpdatePhotoSerializer,
        responses={200: convert_dict_to_serializer({"photo": GetPhotoSerializer()})},
        tags=[SwaggerTags.PHOTO_MANAGEMENT_PHOTOS]
    )
    def patch(self, request, photo_id):
        photo_update_serializer = UpdatePhotoSerializer(data=request.data)
        photo_update_serializer.is_valid(raise_exception=True)

        photo = get_photo(filters={"id": str(photo_id)}, empty_exception=True,
                          user=request.user)
        if not photo_update_serializer.validated_data.get("image"):
            return Response({"result": "Photo was not provided"}, status=204)
        update_photo(photo=photo, data=photo_update_serializer.validated_data)

        return Response({"photo": GetPhotoSerializer(photo, context={'request': request}).data}, status=200)
