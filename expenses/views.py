from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.utils.dateparse import parse_date
from django.db.models import Q, Sum
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from .pagination import CustomPageNumberPagination
from .models import Expense, ExpenseAnalysis, Category
from .serializers import ExpenseSerializer, ErrorResponseSerializer


@extend_schema(
    summary="지출 내역 목록 조회",
    description="지출 내역을 필터링 조건에 따라 조회하고, 페이지네이션된 결과를 반환합니다.",
    parameters=[
        OpenApiParameter(
            name="start_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="조회 시작일",
        ),
        OpenApiParameter(
            name="end_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="조회 종료일",
        ),
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="카테고리명",
        ),
        OpenApiParameter(
            name="date",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="정렬 순서: asc 또는 desc",
        ),
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="페이지 번호",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="한 페이지 당 항목 수",
        ),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            name="성공 응답 예시",
            value={
                "status": "success",
                "data": {
                    "expenses": [
                        {
                            "expense_id": 4306580,
                            "date": "2025-04-30",
                            "amount": 19000,
                            "category": {
                                "id": 92,
                                "name": "잡화/기타",
                                "parent": "기타상품·서비스",
                            },
                            "description": "문구류 쇼핑",
                        },
                        {
                            "expense_id": 4306422,
                            "date": "2025-04-30",
                            "amount": 21000,
                            "category": {
                                "id": 81,
                                "name": "인터넷",
                                "parent": "통신",
                            },
                            "description": "통신요금 납부",
                        },
                    ],
                    "total_amount": 41000,
                    "total_count": 2,
                    "pagination": {
                        "current_page": 1,
                        "page_size": 10,
                        "total_pages": 1,
                        "has_next": False,
                        "has_previous": False,
                    },
                },
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            name="시작일 형식 오류",
            value={
                "status": "error",
                "message": "시작일 형식이 잘못되었습니다",
                "error_code": "INVALID_START_DATE",
            },
            response_only=True,
            status_codes=["400"],
        ),
        OpenApiExample(
            name="종료일 형식 오류",
            value={
                "status": "error",
                "message": "종료일 형식이 잘못되었습니다",
                "error_code": "INVALID_END_DATE",
            },
            response_only=True,
            status_codes=["400"],
        ),
        OpenApiExample(
            name="시작일이 종료일보다 늦음",
            value={
                "status": "error",
                "message": "시작일은 종료일보다 이전이어야 합니다",
                "error_code": "INVALID_DATE_RANGE",
            },
            response_only=True,
            status_codes=["400"],
        ),
    ],
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def index(request):
    # expenses = Expense.objects.filter(user=request.user)
    expenses = Expense.objects.all()  # 테스트용 전체 조회

    # 쿼리 파라미터
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    category_name = request.query_params.get("category")
    date_order = request.query_params.get("date")

    # 날짜 파싱
    parsed_start = parse_date(start_date) if start_date else None
    parsed_end = parse_date(end_date) if end_date else None

    # 오류 체크
    if start_date and not parsed_start:
        raise ValidationError(
            {
                "INVALID_START_DATE": "시작일 형식이 잘못되었습니다",
            }
        )

    if end_date and not parsed_end:
        raise ValidationError(
            {
                "INVALID_END_DATE": "종료일 형식이 잘못되었습니다",
            }
        )

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise ValidationError(
            {
                "INVALID_DATE_RANGE": "시작일은 종료일보다 이전이어야 합니다",
            }
        )

    # 필터링
    if parsed_start:
        expenses = expenses.filter(date__gte=parsed_start)

    if parsed_end:
        expenses = expenses.filter(date__lte=parsed_end)
    if category_name:
        expenses = expenses.filter(
            Q(category__name__iexact=category_name)
            | Q(category__parent_category__name__iexact=category_name)
        )
    if date_order == "asc":
        expenses = expenses.order_by("date")
    elif date_order == "desc":
        expenses = expenses.order_by("-date")
    else:
        expenses = expenses.order_by("-date")

    # 총합, 총건수 계산
    total_count = expenses.count()
    total_amount = expenses.aggregate(sum=Sum("amount")).get("sum") or 0
    total_amount = int(total_amount)

    # 페이지네이션
    paginator = CustomPageNumberPagination()
    page = paginator.paginate_queryset(expenses, request)

    serializer = ExpenseSerializer(page, many=True)

    return Response(
        {
            "status": "success",
            "data": {
                "expenses": serializer.data,
                "total_amount": int(total_amount),
                "total_count": total_count,
                "pagination": {
                    "current_page": paginator.page.number,
                    "page_size": paginator.page.paginator.per_page,
                    "total_pages": paginator.page.paginator.num_pages,
                    "has_next": paginator.page.has_next(),
                    "has_previous": paginator.page.has_previous(),
                },
            },
        }
    )
