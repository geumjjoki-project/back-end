from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.utils.dateparse import parse_date
from django.db.models import Q, Sum

from .pagination import CustomPageNumberPagination
from .models import Expense, ExpenseAnalysis, Category
from .serializers import ExpenseSerializer

# Create your views here.


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
    total_amount = expenses.aggregate(sum=Sum("amount")).get("sum") or 0["total"] or 0
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
