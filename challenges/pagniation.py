from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지당 항목 수
    page_query_param = 'page'  # 쿼리 파라미터 이름: ?page=
    page_size_query_param = 'size'  # 쿼리 파라미터 이름: ?size=
    max_page_size = 100  # size 최대 허용값

    def get_paginated_response(self, data):
        return Response({
            "status": "success",
            "data": data,
            "total_count": self.page.paginator.count
        })
