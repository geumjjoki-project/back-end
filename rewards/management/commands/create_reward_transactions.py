from django.core.management.base import BaseCommand
from django.utils import timezone
from rewards.models import Reward, RewardTransaction
from accounts.models import User
import random
from datetime import timedelta


class Command(BaseCommand):
    help = "'user'로 시작하는 유저 또는 지정한 유저에게 리워드 교환 더미데이터를 bulk_create로 생성 (상태별 날짜 조건 반영)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="특정 username 지정 (예: user1)"
        )
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="유저당 생성할 리워드 교환 수 (기본: 5)"
        )

    def handle(self, *args, **options):
        username_filter = options.get("username")
        count = options["count"]

        if username_filter:
            users = User.objects.filter(username=username_filter)
        else:
            users = User.objects.filter(username__startswith="user")

        if not users.exists():
            self.stdout.write(self.style.ERROR("❌ 대상 유저를 찾을 수 없습니다."))
            return

        rewards = list(Reward.objects.all())
        if not rewards:
            self.stdout.write(self.style.ERROR("❌ 사용 가능한 리워드가 없습니다. 먼저 리워드를 생성하세요."))
            return

        now = timezone.now()
        transactions = []

        for user in users:
            for _ in range(count):
                reward = random.choice(rewards)
                status = random.choice([0, 1, 2, 3])

                if status == 2:  # 만료
                    expire_at = now - timedelta(days=random.randint(1, 10))
                    redeemed_at = expire_at - timedelta(days=random.randint(1, reward.valid_days))
                elif status == 0:  # 이용 가능
                    redeemed_at = now - timedelta(days=random.randint(0, reward.valid_days - 1))
                    expire_at = redeemed_at + timedelta(days=reward.valid_days)
                    if expire_at <= now:
                        expire_at = now + timedelta(days=random.randint(1, 5))  # 보장
                else:  # 사용완료, 중지
                    redeemed_at = now - timedelta(days=random.randint(0, 30))
                    expire_at = redeemed_at + timedelta(days=reward.valid_days)

                # 보장: 만료일은 시작일보다 반드시 뒤여야 함
                if expire_at <= redeemed_at:
                    expire_at = redeemed_at + timedelta(days=1)

                transactions.append(RewardTransaction(
                    user=user,
                    reward=reward,
                    status=status,
                    redeemed_at=redeemed_at,
                    expire_at=expire_at,
                ))
            self.stdout.write(self.style.SUCCESS(f"✅ {user.username} 트랜잭션 준비 완료"))

        RewardTransaction.objects.bulk_create(transactions, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"🎉 총 {len(transactions)}개의 리워드 교환 더미데이터 생성 완료"))
