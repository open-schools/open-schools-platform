from django.urls import path

from open_schools_platform.organization_management.teachers.views import GetTeacherProfileApi

urlpatterns = [
    path('/teacher-profile/<uuid:pk>', GetTeacherProfileApi.as_view(), name='get-teacher-profile')
]
