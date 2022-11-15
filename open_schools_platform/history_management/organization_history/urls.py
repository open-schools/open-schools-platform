from django.urls import path

from open_schools_platform.history_management.organization_history.views import HistoryApi

urlpatterns = [
    path('<uuid:pk>', HistoryApi.as_view(), name='organization_history')
]
