from django.urls import path

from open_schools_platform.student_management.students.views import StudentProfileApi, AutoStudentJoinCircleQueryApi, \
    StudentJoinCircleQueryUpdateApi, StudentQueriesListApi, StudentCirclesListApi, StudentProfileUpdateApi, \
    StudentJoinCircleQueryApi

urlpatterns = [
    path('student-profile', StudentProfileApi.as_view(), name='create-student-profile'),
    path('student-profile/<uuid:pk>', StudentProfileUpdateApi.as_view(), name='update-student-profile'),
    path('student-profile-generate/student-join-cricle-query', AutoStudentJoinCircleQueryApi.as_view(),
         name='auto-student-join-circle-query'),
    path('student-profile/<uuid:pk>/student-join-circle-query', StudentJoinCircleQueryApi.as_view(),
         name='student-join-circle-query'),
    path('student-join-circle-query', StudentJoinCircleQueryUpdateApi.as_view(),
         name='student-join-circle-update-query'),
    path('student-profile/<uuid:pk>/queries', StudentQueriesListApi.as_view(), name='queries-list'),
    path('student-profile/<uuid:pk>/circles', StudentCirclesListApi.as_view(), name='circles-list')
]
