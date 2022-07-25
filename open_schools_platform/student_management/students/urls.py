from django.urls import path

from open_schools_platform.student_management.students.views import StudentProfileApi, StudentJoinCircleQueryApi

urlpatterns = [
    path('students-profile', StudentProfileApi.as_view(), name='create-students-profile'),
    path('students-join-cricle-query', StudentJoinCircleQueryApi.as_view(),
         name='students-join-circle-query')
]
