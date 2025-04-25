from rest_framework.pagination import PageNumberPagination


# 리워드 페이지네이션
# 10개 고정
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = None
