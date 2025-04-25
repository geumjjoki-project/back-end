from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework import status


# 페이지네이션
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20  # 기본 페이지 크기
    page_size_query_param = "page_size"  # 쿼리 파라미터 이름
    max_page_size = 100  # 최대 페이지 크기
    allowed_page_sizes = [10, 20, 30, 50, 100]  # 허용 페이지 크기 목록

    def get_page_size(self, request):
        raw = request.query_params.get(self.page_size_query_param)
        if raw is None:
            return self.page_size

        try:
            page_size = int(raw)
        except ValueError:
            raise ValidationError(
                {
                    "invalid_page_size": "page_size는 숫자여야 합니다.",
                }
            )

        if page_size not in self.allowed_page_sizes:
            raise ValidationError(
                {
                    "unsupported_page_size": f"허용된 page_size 값만 사용 가능합니다: {self.allowed_page_sizes}",
                }
            )

        return page_size
