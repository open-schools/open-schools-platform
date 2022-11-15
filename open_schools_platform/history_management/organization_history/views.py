from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.history_management.organization_history.serializers import OrganizationHistorySerializer
from open_schools_platform.organization_management.organizations.selectors import get_organization
from open_schools_platform.common.views import swagger_dict_response


class HistoryApi(APIView):
    @swagger_auto_schema(
        operation_description="Get organization history.",
        tags=[SwaggerTags.HISTORY_MANAGEMENT],
        responses={200: swagger_dict_response({'results': OrganizationHistorySerializer(many=True)}),
                   404: "There is no such organization"},
    )
    def get(self, request, pk):
        organization = get_organization(filters={"id": pk},
                                        empty_exception=True,
                                        empty_message="There is no such organization")
        return Response({"results": OrganizationHistorySerializer(organization).data}, status=200)
