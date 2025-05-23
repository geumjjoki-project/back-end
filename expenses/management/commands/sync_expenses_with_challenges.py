from django.core.management.base import BaseCommand
from challenges.models import UserChallenge
from expenses.models import Expense
from django.db.models import Q, Sum

class Command(BaseCommand):
    help = "기존 지출내역과 유저챌린지를 챌린지 기간/카테고리 기준으로 자동 연결합니다."

    def handle(self, *args, **options):
        for uc in UserChallenge.objects.all():
            challenge = uc.challenge
            category = challenge.category
            root_category = category.get_root_category() if category else None

            expenses_qs = Expense.objects.filter(
                user=uc.user,
                date__gte=uc.start_date.date(),
                date__lte=uc.end_date.date(),
            )
            if root_category:
                expenses_qs = expenses_qs.filter(
                    Q(category=root_category) | Q(category__parent_category=root_category)
                )

            expenses_count = expenses_qs.count()
            expenses_qs.update(user_challenge=uc)

            total = expenses_qs.aggregate(total=Sum("amount"))["total"] or 0
            uc.total_expense = total
            uc.save(update_fields=["total_expense"])

            self.stdout.write(
                f"UserChallenge(id={uc.pk}) - {expenses_count}개의 지출내역 연결, 누적지출 {total}원으로 갱신"
            )
        self.stdout.write(self.style.SUCCESS('지출내역-유저챌린지 동기화가 완료되었습니다.'))
