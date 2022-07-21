from django.urls import path, include


query_management_urls = [
    path('queries/', include(('open_schools_platform.query_management.queries.urls', 'queries'))),
]

parent_management_urls = [
    path('families/', include(('open_schools_platform.parent_management.families.urls', 'families'))),
]

user_management_urls = [
    path('users/', include(('open_schools_platform.user_management.users.urls', 'users'))),
    path(
        'auth/', include(('open_schools_platform.user_management.authentication.urls', 'authentication'))
    ),
]

organization_management_urls = [
    path('organizations/',
         include(('open_schools_platform.organization_management.organizations.urls', 'organizations'))),
    path('employees/',
         include(('open_schools_platform.organization_management.employees.urls', 'employees'))),
    path('circles/',
         include(('open_schools_platform.organization_management.circles.urls', 'circles'))),
]

urlpatterns = [
    path('user-management/', include((user_management_urls, "user-management"))),
    path('organization-management/', include(organization_management_urls)),
    path('query-management/', include((query_management_urls, 'query-management'))),
    path('errors/', include(('open_schools_platform.errors.urls', 'errors'))),
    path('parent-management/', include((parent_management_urls, "parent-management"))),
    path('student-management/', include(('open_schools_platform.student_management.student.urls',
                                         'student-management')))
]
