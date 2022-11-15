from django.urls import path

from open_schools_platform.history_management.student_history.views import HistoryApi

urlpatterns = [
    path('<uuid:pk>', HistoryApi.as_view(), name='student_history')
]
