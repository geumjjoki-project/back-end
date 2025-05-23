from datetime import date
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Expense, Category
from .serializers import ExpenseSerializer, ExpenseWriteSerializer, CategorySerializer
from .pagination import CustomPageNumberPagination

from django.db.models import Sum

from expenses.utils.date import validate_and_parse_dates
from expenses.utils.query import get_ordering, get_category_filter_q
from expenses.utils.response import success_response, error_response
from expenses.utils.summarize import summarize

from challenges.models import UserChallenge

class ExpenseBaseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class ExpenseListView(ExpenseBaseView):
    def get(self, request):
        user = request.user
        query = request.query_params

        start_date = query.get("start_date")
        end_date = query.get("end_date")
        category_names = query.getlist("category") or query.getlist("category[]")
        include_null_category = query.get("include_null_category") == "true"
        date_order = query.get("date", "desc")
        description = query.get("description")

        parsed_start, parsed_end = validate_and_parse_dates(start_date, end_date)

        base_q = Q(user=user)
        if parsed_start:
            base_q &= Q(date__gte=parsed_start)
        if parsed_end:
            base_q &= Q(date__lte=parsed_end)
        if description:
            base_q &= Q(description__icontains=description)

        category_q = Q()
        if category_names:
            category_q |= get_category_filter_q(category_names)
        if include_null_category:
            category_q |= Q(category__isnull=True)

        if category_q.children:
            expenses = Expense.objects.filter(base_q & category_q)
        else:
            expenses = Expense.objects.filter(base_q)

        order_field = get_ordering("date", date_order)
        expenses = expenses.order_by(order_field)

        total_count = expenses.count()
        total_amount = int(expenses.aggregate(sum=Sum("amount")).get("sum") or 0)

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(expenses, request)
        serializer = ExpenseSerializer(page, many=True)

        return success_response({
            "expenses": serializer.data,
            "total_amount": total_amount,
            "total_count": total_count,
            "pagination": {
                "current_page": paginator.page.number,
                "page_size": paginator.page.paginator.per_page,
                "total_pages": paginator.page.paginator.num_pages,
                "has_next": paginator.page.has_next(),
                "has_previous": paginator.page.has_previous(),
            },
        })
        
class ExpenseDetailView(ExpenseBaseView):
    def get_object(self, expense_id, user):
        try:
            expense = Expense.objects.get(expense_id=expense_id)
        except Expense.DoesNotExist:
            raise NotFound("지출 내역을 찾을 수 없습니다.")

        if expense.user != user:
            raise PermissionDenied("지출 내역에 접근할 권한이 없습니다.")
        return expense

    def get(self, request, expense_id):
        expense = self.get_object(expense_id, request.user)
        serializer = ExpenseSerializer(expense)
        return success_response(serializer.data)

    def put(self, request, expense_id):
        expense = self.get_object(expense_id, request.user)
        if expense.user_challenge is not None:
            return error_response(
                message="챌린지에 연결된 지출내역은 수정할 수 없습니다.",
                error_code="CHALLENGE_LOCKED_EXPENSE",
                status_code=400
            )
        serializer = ExpenseWriteSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data)
        return error_response(
            message="입력값이 유효하지 않습니다.",
            error_code="INVALID_INPUT",
            status_code=400
        )

    def delete(self, request, expense_id):
        expense = self.get_object(expense_id, request.user)
        if expense.user_challenge is not None:
            return error_response(
                message="챌린지에 연결된 지출내역은 삭제할 수 없습니다.",
                error_code="CHALLENGE_LOCKED_EXPENSE",
                status_code=400
            )
        expense.delete()
        return success_response({
            "message": "지출 내역이 삭제되었습니다."
        })
        
class ExpenseSummaryView(ExpenseBaseView):
    def get(self, request):
        user = request.user
        year = int(request.GET.get("year", date.today().year))
        month = int(request.GET.get("month", date.today().month))

        # 이전 달 계산
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        # 데이터 조회
        expenses_this = Expense.objects.filter(user=user, date__year=year, date__month=month)
        expenses_prev = Expense.objects.filter(user=user, date__year=prev_year, date__month=prev_month)

        # 루트 카테고리 이름 목록
        all_roots = Category.objects.filter(parent_category__isnull=True)
        all_root_names = list(all_roots.values_list("name", flat=True)) + ["미분류"]

        # 요약 계산
        total_this, category_this = summarize(expenses_this, all_root_names)
        total_prev, category_prev = summarize(expenses_prev, all_root_names)

        return success_response({
            "current_month": {
                "year": year,
                "month": month,
                "total_amount": total_this,
                "category_summary": category_this,
            },
            "previous_month": {
                "year": prev_year,
                "month": prev_month,
                "total_amount": total_prev,
                "category_summary": category_prev,
            }
        })
        
        
class ExpenseCreateView(ExpenseBaseView):
    def post(self, request):
        serializer = ExpenseWriteSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.validated_data.get('category')
            user = request.user
            expense_date = serializer.validated_data.get('date')

            user_challenges = UserChallenge.objects.filter(
                user=user,
                status='도전중',
                start_date__date__lte=expense_date,
                end_date__date__gte=expense_date,
            )
            user_challenge = None
            if category is not None:
                from django.db.models import Q
                root_category = category.get_root_category() if hasattr(category, "get_root_category") else category
                user_challenges = user_challenges.filter(
                    Q(challenge__category=category) | Q(challenge__category=root_category) | Q(challenge__category__parent_category=root_category)
                )
            if user_challenges.exists():
                user_challenge = user_challenges.first()

            expense = serializer.save(user=user, user_challenge=user_challenge)
            return success_response(ExpenseSerializer(expense).data, status_code=201)
        return error_response(
            message="입력값이 유효하지 않습니다.",
            error_code="INVALID_INPUT",
            status_code=400
        )
        
class RootCategoryListView(ExpenseBaseView):
    def get(self, request):
        queryset = Category.objects.filter(parent_category__isnull=True)
        serializer = CategorySerializer(queryset, many=True)
        return success_response(serializer.data)