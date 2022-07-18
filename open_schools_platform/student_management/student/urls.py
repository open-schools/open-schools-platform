from django.urls import path

from open_schools_platform.student_management.student.views import StudentProfileApi, StudentJoinCircleInquiryApi

urlpatterns = [
    path('student-profile', StudentProfileApi.as_view(), name='create-student-profile'),
    path('<uuid:pk>/student-join-cricle-inquiry', StudentJoinCircleInquiryApi.as_view(),
         name='student-join-circle-inquiry')
]
