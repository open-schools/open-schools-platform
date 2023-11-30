from django.urls import path

from open_schools_platform.query_management.queries.views import QueryStatusChangeApi, QueryChangesHistoryApi

urlpatterns = [
    path('', QueryStatusChangeApi.as_view(), name='change-query-status'),
    path('/<uuid:query_id>/changes', QueryChangesHistoryApi.as_view(), name='query-status-changes'),
]
