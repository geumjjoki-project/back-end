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


class Command(BaseCommand):
    help = "지정한 id의 유저 4월 한달(30일) 지출 더미데이터 생성"

    def add_arguments(self, parser):
        parser.add_argument(
            'user_id',
            type=int,
            nargs='?',
            help='유저 id (예: 1)'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        if user_id is None:
            self.stdout.write(self.style.WARNING(
                "사용법: python manage.py <command_name> <user_id>\n예: python manage.py create_expenses 1"
            ))
            return

        User = get_user_model()
        
        # 1) 해당 유저 및 프로필
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"id={user_id}인 사용자가 없습니다."))
            return

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"id={user_id} 유저 프로필이 없습니다."))
            return

        # 2) 서브(leaf) 카테고리만 로드
        leaf_list = list(Category.objects.filter(child_category__isnull=True))
        if not leaf_list:
            self.stdout.write(self.style.ERROR("서브 카테고리가 없습니다."))
            return

        expense_objs = []
        BATCH_SIZE = 1000

        # 3) 4월 한 달(30일) 동안 반복
        start_date = datetime(2025, 4, 1).date()
        end_date = datetime(2025, 4, 30).date()
        num_days = (end_date - start_date).days + 1

        # 기존 데이터 삭제 (옵션)
        Expense.objects.filter(user=user, date__range=[start_date, end_date]).delete()

        for i in range(num_days):
            current_date = start_date + timedelta(days=i)
            num_expenses_today = random.randint(1, 3)  # 하루에 1~3건
            for _ in range(num_expenses_today):
                cat = random.choice(leaf_list)
                cost = Decimal(random.randint(5, 30)) * 1000  # 5,000~30,000원
                expense_objs.append(
                    Expense(
                        user=user,
                        category=cat,
                        description=generate_description(cat),
                        amount=cost,
                        date=current_date,
                    )
                )

        with transaction.atomic():
            Expense.objects.bulk_create(expense_objs, batch_size=BATCH_SIZE)

        self.stdout.write(self.style.SUCCESS(
            f"✅   id={user_id} 유저({user.username}) 4월 한달 더미 지출 생성 완료 ({len(expense_objs)}건)"
        ))
