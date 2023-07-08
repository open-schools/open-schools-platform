from rest_framework.pagination import PageNumberPagination


class ApiStudentsListPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = 'page_size'
    max_page_size = 500


class ApiStudentProfilesListPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = 'page_size'
    max_page_size = 500
