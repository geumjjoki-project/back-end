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
    root = cat.get_root_category().name
    sub = cat.name
    try:
        candidates = categories_data[root][sub]
        if isinstance(candidates, list) and candidates:
            return random.choice(candidates)
    except (KeyError, TypeError):
        pass
    return f"{sub} 결제"


def random_date_in_month(year, month, start_date, end_date):
    """해당 월 내에서 랜덤 날짜 생성"""
    # 월의 첫날과 마지막날 계산
    if start_date.year == year and start_date.month == month:
        month_start = start_date
    else:
        month_start = datetime(year, month, 1).date()
    if end_date.year == year and end_date.month == month:
        month_end = end_date
    else:
        if month == 12:
            month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
    delta_days = (month_end - month_start).days
    if delta_days < 0:
        raise ValueError("월 내의 날짜 범위가 잘못되었습니다.")
    return month_start + timedelta(days=random.randint(0, delta_days))


class Command(BaseCommand):
    help = "UserProfile.average_income 기준으로 각 월별 평균수입을 넘지 않도록, 지정 기간의 Expense를 여러 사용자 대상으로 bulk 생성"

    def add_arguments(self, parser):
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

    def handle(self, *args, **options):
        User = get_user_model()

        # 서브(leaf) 카테고리 로드
        leaf_list = list(Category.objects.filter(child_category__isnull=True))
        if not leaf_list:
            self.stdout.write(self.style.ERROR("서브 카테고리가 없습니다."))
            return

        # user 계정 쿼리
        profiles = UserProfile.objects.select_related("user").filter(
            user__username__startswith="user"
        )
        total_users = profiles.count()
        self.stdout.write(f"총 {total_users}명 사용자에 대해 생성을 시작합니다…")

        # 날짜 옵션 파싱
        today = datetime.now().date()
        enddate_str = options.get('enddate')
        startdate_str = options.get('startdate')
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
        Expense.objects.filter(
            user__in=[p.user for p in profiles], date__range=[start_date, end_date]
        ).delete()

        expense_objs = []
        BATCH_SIZE = 10000

        with transaction.atomic():
            for idx, prof in enumerate(profiles.iterator(), start=1):
                user = prof.user
                income = prof.average_income

                current_date = start_date
                while current_date <= end_date:
                    year, month = current_date.year, current_date.month
                    # 월 시작일/마지막일 구하기
                    if month == 12:
                        next_month = datetime(year + 1, 1, 1).date()
                    else:
                        next_month = datetime(year, month + 1, 1).date()
                    month_start = max(current_date, datetime(year, month, 1).date())
                    month_end = min(next_month - timedelta(days=1), end_date)

                    monthly_total = Decimal('0.00')
                    temp_expenses = []
                    # 날짜 리스트 미리 준비해서 랜덤 샘플링에 사용(지출건수와 관계 없음)
                    day_list = [
                        month_start + timedelta(days=i)
                        for i in range((month_end - month_start).days + 1)
                    ]
                    day_idx = 0
                    while monthly_total < income and day_idx < len(day_list):
                        day = day_list[day_idx]
                        num_expenses_today = random.randint(1, 3)
                        for _ in range(num_expenses_today):
                            cat = random.choice(leaf_list)
                            cost = Decimal(random.randint(5, 30)) * 1000  # 5,000~30,000원
                            if monthly_total + cost > income:
                                cost = income - monthly_total
                                if cost <= 0:
                                    break
                            temp_expenses.append(
                                Expense(
                                    user=user,
                                    category=cat,
                                    description=generate_description(cat),
                                    amount=cost,
                                    date=day,
                                )
                            )
                            monthly_total += cost
                            if monthly_total >= income:
                                break
                        day_idx += 1

                    expense_objs.extend(temp_expenses)

                    # 다음 달 1일로 이동
                    current_date = next_month

                # 배치 단위로 bulk_create
                if len(expense_objs) >= BATCH_SIZE:
                    Expense.objects.bulk_create(expense_objs, batch_size=BATCH_SIZE)
                    expense_objs.clear()

                # 1,000명 단위로 진행률 출력
                if idx % 1000 == 0 or idx == total_users:
                    self.stdout.write(f"[{idx}/{total_users}] 사용자 지출 생성 완료")

            # 남은 객체들 삽입
            if expense_objs:
                Expense.objects.bulk_create(expense_objs, batch_size=BATCH_SIZE)

        self.stdout.write(self.style.SUCCESS("✅   모든 지출 내역 bulk 생성 완료"))
