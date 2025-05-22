import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware, now

from challenges.models import Challenge
from expenses.models import Category

CATEGORY_NAMES = ["술·담배", "옷", "외식·숙박", "여가"]

def generate_challenge_period(goal_days):
    """
    목표일수에 따라 운영기간 생성
    - 7일 목표 → 약 30일 운영
    - 28일 목표 → 약 90일 운영
    """
    period_length = 29 if goal_days == 7 else 89
    start_offset = random.randint(-5, 5)  # 현재 기준 ±5일 내에서 시작
    start_date = make_aware(datetime.now() + timedelta(days=start_offset))
    end_date = start_date + timedelta(days=period_length)
    return start_date, end_date

def determine_status(start, end, current_time):
    """현재 시각 기준으로 챌린지 상태 결정"""
    if current_time < start:
        return "예정"
    elif start <= current_time <= end:
        return "진행중"
    else:
        return "종료"

class Command(BaseCommand):
    help = "카테고리별로 챌린지 더미 데이터를 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='카테고리별 생성할 챌린지 수 (기본값: 3)'
        )

    def handle(self, *args, **options):
        count = options['count']
        categories = {}

        for name in CATEGORY_NAMES:
            try:
                category = Category.objects.get(name=name)
                categories[name] = category
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"[{name}] 카테고리를 찾을 수 없습니다."))

        if not categories:
            self.stdout.write(self.style.ERROR("유효한 카테고리가 없습니다. 챌린지를 생성할 수 없습니다."))
            return

        current_time = now()
        total_created = 0

        for name, category in categories.items():
            for i in range(count):
                # 목표일수 선택: 7일 또는 28일
                goal_days = random.choice([7, 28])
                start_date, end_date = generate_challenge_period(goal_days)
                status = determine_status(start_date, end_date, current_time)
                point = random.choice([i for i in range(100, 1001, 100)])

                title_suffix = "일주일" if goal_days == 7 else "한 달"
                challenge = Challenge.objects.create(
                    title=f"[{name}] {title_suffix} 소비 줄이기 챌린지 #{i+1}",
                    content=f"{name} 소비를 {title_suffix} 동안 줄여보세요!",
                    category=category,
                    point=point,
                    goal_days=goal_days,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                )
                self.stdout.write(self.style.SUCCESS(f"{name} #{i+1} [{status}] 생성됨: {challenge.title}"))
                total_created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ 총 {total_created}개의 챌린지가 생성되었습니다."))
