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


def random_date_in_april():
    start = datetime(2025, 4, 1)
    end = datetime(2025, 4, 30)
    delta_days = (end - start).days
    return (start + timedelta(days=random.randint(0, delta_days))).date()


class Command(BaseCommand):
    help = "UserProfile.average_income 기준으로 4월분 Expense를 bulk 생성하며 1,000명 단위로 진행률 출력"

    def handle(self, *args, **options):
        User = get_user_model()

        # 1) 서브(leaf) 카테고리만 로드
        leaf_list = list(Category.objects.filter(child_category__isnull=True))
        if not leaf_list:
            self.stdout.write(self.style.ERROR("서브 카테고리가 없습니다."))
            return

        # 2) user{i} 프로필 쿼리셋 및 전체 수
        profiles = UserProfile.objects.select_related("user").filter(
            user__username__startswith="user"
        )
        total_users = profiles.count()
        self.stdout.write(f"총 {total_users}명 사용자에 대해 생성을 시작합니다…")

        expense_objs = []
        BATCH_SIZE = 10000

        with transaction.atomic():
            for idx, prof in enumerate(profiles.iterator(), start=1):
                user = prof.user
                income = prof.average_income
                spent = Decimal("0.00")

                # 한 사용자의 지출 내역 생성
                while spent < income:
                    cost = Decimal(random.randint(10, 500) * 100)
                    if spent + cost > income:
                        cost = income - spent
                        if cost <= 0:
                            break

                    cat = random.choice(leaf_list)

                    expense_objs.append(
                        Expense(
                            user=user,
                            category=cat,
                            description=generate_description(cat),
                            amount=cost,
                            date=random_date_in_april(),
                        )
                    )
                    spent += cost

                # 배치 단위로 bulk_create
                if len(expense_objs) >= BATCH_SIZE:
                    with transaction.atomic():
                        Expense.objects.bulk_create(expense_objs, batch_size=BATCH_SIZE)
                    expense_objs.clear()

                # 1,000명 단위로 진행률 출력
                if idx % 1000 == 0 or idx == total_users:
                    self.stdout.write(f"[{idx}/{total_users}] 사용자 지출 생성 완료")

            # 남은 객체들 삽입
            if expense_objs:
                Expense.objects.bulk_create(expense_objs, batch_size=BATCH_SIZE)

        self.stdout.write(self.style.SUCCESS("✅   모든 지출 내역 bulk 생성 완료"))
