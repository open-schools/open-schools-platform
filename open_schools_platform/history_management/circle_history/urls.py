from django.urls import path

from open_schools_platform.history_management.circle_history.views import HistoryApi

urlpatterns = [
    path('<uuid:pk>', HistoryApi.as_view(), name='circle_history')
]