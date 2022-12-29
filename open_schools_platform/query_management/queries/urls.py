from django.urls import path

from open_schools_platform.query_management.queries.views import QueryStatusChangeApi

urlpatterns = [
    path('', QueryStatusChangeApi.as_view(), name='change-query-status'),
]
