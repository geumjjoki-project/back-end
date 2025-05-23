from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomRewardPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data, extra=None):
        pagination = {
            "current_page": self.page.number,
            "page_size": self.page.paginator.per_page,
            "total_pages": self.page.paginator.num_pages,
            "has_next": self.page.has_next(),
            "has_previous": self.page.has_previous(),
        }
        response_data = {
            "rewards": data,
            "total_count": self.page.paginator.count,
            "pagination": pagination,
        }
        if extra:
            response_data.update(extra)
        return Response(response_data)