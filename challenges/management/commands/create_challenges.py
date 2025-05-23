import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from challenges.models import Challenge
from expenses.models import Category

CATEGORY_NAMES = ["술·담배", "옷", "외식·숙박", "여가"]

CHALLENGE_PRESETS = [
    {"goal_days": 7, "goal_amount": 10000, "point": 50},
    {"goal_days": 7, "goal_amount": 30000, "point": 150},
    {"goal_days": 7, "goal_amount": 50000, "point": 250},
    {"goal_days": 28, "goal_amount": 100000, "point": 500},
    {"goal_days": 28, "goal_amount": 200000, "point": 1000},
]

STATE_DISTRIBUTION = {
    "예정": 6,
    "도전가능": 6,
    "도전불가": 2,
    "종료": 6,
}

def assign_states_fixed(total, state_distribution):
    state_pool = []
    for state, count in state_distribution.items():
        state_pool += [state] * count
    random.shuffle(state_pool)
    return state_pool

def generate_period_by_status(goal_days, state):
    period_length = 29 if goal_days == 7 else 89
    today = now()

    if state == "예정":
        start_date = today + timedelta(days=random.randint(5, 15))
    elif state == "도전가능":
        start_date = today - timedelta(days=random.randint(1, goal_days - 3))
    elif state == "도전불가":
        end_date = today + timedelta(days=random.randint(1, 2))
        start_date = end_date - timedelta(days=goal_days - 1)
        return start_date, end_date
    else:  # 종료
        start_date = today - timedelta(days=goal_days + random.randint(5, 30))

    start_date = start_date
    end_date = start_date + timedelta(days=period_length)
    return start_date, end_date

class Command(BaseCommand):
    help = "챌린지 더미 데이터를 생성합니다 (computed_status 테스트 포함)"

    def handle(self, *args, **options):
        categories = {}
        for name in CATEGORY_NAMES:
            try:
                categories[name] = Category.objects.get(name=name)
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"{name} 카테고리를 찾을 수 없습니다."))

        if not categories:
            self.stdout.write(self.style.ERROR("카테고리를 찾을 수 없어 챌린지를 생성할 수 없습니다."))
            return

        targets = []
        for name, category in categories.items():
            for preset in CHALLENGE_PRESETS:
                targets.append({
                    "category_name": name,
                    "category": category,
                    "goal_days": preset["goal_days"],
                    "goal_amount": preset["goal_amount"],
                    "point": preset["point"],
                })

        state_pool = assign_states_fixed(len(targets), STATE_DISTRIBUTION)

        total_created = 0
        for i, data in enumerate(targets):
            raw_status = state_pool[i]
            start_date, end_date = generate_period_by_status(data["goal_days"], raw_status)

            title_suffix = "일주일" if data["goal_days"] == 7 else "한 달"
            content = f"{data['category_name']} 지출을 {title_suffix} 동안 {data['goal_amount']:,}원 이하로 줄이기"

            challenge = Challenge.objects.create(
                title=f"[{data['category_name']}] {title_suffix} 소비 줄이기 - {data['goal_amount'] // 10000}만원",
                content=content,
                category=data["category"],
                goal_amount=data["goal_amount"],
                point=data["point"],
                goal_days=data["goal_days"],
                is_active=True,
                start_date=start_date,
                end_date=end_date,
            )

            self.stdout.write(self.style.SUCCESS(
                f"{challenge.title} | 테스트 상태: {raw_status} | 실제 상태: {challenge.computed_status} | 기간: {start_date.date()} ~ {end_date.date()}"
            ))
            total_created += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ 총 {total_created}개의 챌린지가 생성되었습니다."))
