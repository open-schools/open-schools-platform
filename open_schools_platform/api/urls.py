from django.urls import path, include

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
]

urlpatterns = [
    path('user-management/', include((user_management_urls, "user-management"))),
    path('organization-management/', include(organization_management_urls)),
    path('errors/', include(('open_schools_platform.errors.urls', 'errors'))),
    path('parent-management/', include((parent_management_urls, "parent-management"))),
    path('student-management/', include(('open_schools_platform.student_management.student_profile.urls',
                                         'student-profile')))
]
