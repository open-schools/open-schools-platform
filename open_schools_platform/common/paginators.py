from rest_framework.pagination import PageNumberPagination


class DefaultListPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = 'page_size'
    max_page_size = 500
