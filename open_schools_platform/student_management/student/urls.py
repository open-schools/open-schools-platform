from django.urls import path

from open_schools_platform.student_management.student.views import StudentProfileApi, StudentJoinCircleQueryApi, \
    StudentJoinCircleQueryUpdateApi, StudentCirclesListApi, StudentQueriesListApi

urlpatterns = [
    path('student-profile', StudentProfileApi.as_view(), name='create-student-profile'),
    path('<uuid:pk>/student-join-cricle-query', StudentJoinCircleQueryApi.as_view(),
         name='student-join-circle-query'),
    path('student-join-circle-query', StudentJoinCircleQueryUpdateApi.as_view(),
         name='student-join-circle-update-query'),
    path('queries', StudentQueriesListApi.as_view(), name='queries-list'),
    path('circles', StudentCirclesListApi.as_view(), name='circles-list')
]
