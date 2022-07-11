from django.urls import path

from open_schools_platform.query_management.queries.views import QueryStatusChangeApi

urlpatterns = [
    path("queries/", QueryStatusChangeApi.as_view(), name="query-status")
]
