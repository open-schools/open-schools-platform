from django.urls import path

from open_schools_platform.student_management.student.views import StudentProfileApi, StudentJoinCircleApi

urlpatterns = [
    path('student-profile', StudentProfileApi.as_view(), name='create_student_profile'),
    path('<uuid:pk>/student-join-circle', StudentJoinCircleApi.as_view(),
         name='student_join_circle')
]
