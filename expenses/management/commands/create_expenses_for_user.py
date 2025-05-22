import random
from decimal import Decimal
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import UserProfile
from expenses.models import Category, Expense

from expenses.utils.category_descriptions import categories_data

def generate_description(cat):
    if cat is None:
        return "미분류 지출"
    root = cat.get_root_category().name
    sub = cat.name
    try:
        candidates = categories_data[root][sub]
        if isinstance(candidates, list) and candidates:
            return random.choice(candidates)
    except (KeyError, TypeError):
        pass
    return f"{sub} 결제"

class Command(BaseCommand):
    help = "지정한 username의 유저에 대해 지정 기간의 지출 더미데이터 생성 (기본: 최근 2개월, 월별 평균수입 이하로만 생성, 미분류 비율 옵션 포함)"

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            nargs='?',
            help='유저 username (예: johndoe)'
        )
        parser.add_argument(
            '--startdate',
            type=str,
            default=None,
            help='시작 날짜 (YYYY-MM-DD, 기본값: 오늘로부터 2개월 전)'
        )
        parser.add_argument(
            '--enddate',
            type=str,
            default=None,
            help='종료 날짜 (YYYY-MM-DD, 기본값: 오늘)'
        )
        parser.add_argument(
            '--unclassified-ratio',
            type=float,
            default=0.01,  # 1% 기본값
            help='미분류(카테고리 없음) 지출 생성 비율 (기본 0.01)'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        startdate_str = options.get('startdate')
        enddate_str = options.get('enddate')
        percent_unclassified = options.get('unclassified_ratio', 0.01)

        if username is None:
            self.stdout.write(self.style.WARNING(
                "사용법: python manage.py <command_name> <username> [--startdate YYYY-MM-DD] [--enddate YYYY-MM-DD] [--unclassified-ratio 0.01]\n"
                "예: python manage.py create_expenses johndoe --startdate 2025-03-01 --enddate 2025-04-30 --unclassified-ratio 0.02"
            ))
            return

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"username={username} 인 사용자가 없습니다."))
            return

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"username={username} 유저 프로필이 없습니다."))
            return

        leaf_list = list(Category.objects.filter(child_category__isnull=True))
        if not leaf_list:
            self.stdout.write(self.style.ERROR("서브 카테고리가 없습니다."))
            return

        # 날짜 기본값 처리 (기본: 최근 2개월)
        today = datetime.now().date()
        if enddate_str:
            end_date = datetime.strptime(enddate_str, "%Y-%m-%d").date()
        else:
            end_date = today

        if startdate_str:
            start_date = datetime.strptime(startdate_str, "%Y-%m-%d").date()
        else:
            start_date = end_date - timedelta(days=59)

        if end_date < start_date:
            self.stdout.write(self.style.ERROR("종료일이 시작일보다 빠릅니다."))
            return

        # 기존 데이터 삭제
        Expense.objects.filter(user=user, date__range=[start_date, end_date]).delete()

        average_income = profile.average_income
        BATCH_SIZE = 1000
        expense_objs = []

        current_date = start_date
        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1, day=1)
            month_end = min(next_month - timedelta(days=1), end_date)
            
            monthly_total = Decimal(0)
            temp_expenses = []
            day = current_date
            while day <= month_end:
                num_expenses_today = random.randint(1, 3)
                for _ in range(num_expenses_today):
                    # 일정 확률로 미분류(category=None) 처리
                    if random.random() < percent_unclassified:
                        cat = None
                    else:
                        cat = random.choice(leaf_list)
                    cost = Decimal(random.randint(5, 30)) * 1000  # 5,000~30,000원
                    if monthly_total + cost > average_income:
                        day = next_month  # 바로 다음 달로 이동
                        break
                    expense = Expense(
                        user=user,
                        category=cat,
                        description=generate_description(cat),
                        amount=cost,
                        date=day,
                    )
                    temp_expenses.append(expense)
                    monthly_total += cost
                else:
                    day += timedelta(days=1)
                    continue
                break
            expense_objs.extend(temp_expenses)
            current_date = next_month

        with transaction.atomic():
            Expense.objects.bulk_create(expense_objs, batch_size=BATCH_SIZE)

        self.stdout.write(self.style.SUCCESS(
            f"✅   username={username} 유저({user.username}) {start_date}~{end_date} (월별 {average_income} 이하, 미분류 비율 {percent_unclassified:.2%}) 더미 지출 생성 완료 ({len(expense_objs)}건)"
        ))
