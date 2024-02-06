from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 4
    max_page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        return super().paginate_queryset(queryset, request, view=None)

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'data': data
        })


class CustomCursorPagination(CursorPagination):
    ordering = '-starting_date'
    page_size = 5
    page_size_query_param = 'page_size'
