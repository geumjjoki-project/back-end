from django.core.management.base import BaseCommand
from expenses.models import Category


class Command(BaseCommand):
    help = "KOSIS 기반 자기참조 카테고리 구조를 생성합니다."

    def handle(self, *args, **kwargs):
        categories_data = {
            "식품": ["마트", "편의점", "음료수"],
            "술·담배": ["소주", "맥주", "담배"],
            "옷": ["상의", "하의", "신발"],
            "주거비": ["월세", "전기세", "수도요금"],
            "집안살림": ["청소용품", "세탁", "인테리어소품"],
            "의료": ["병원진료", "약국", "건강보조제"],
            "교통": ["대중교통", "택시", "주유"],
            "통신": ["휴대폰", "인터넷"],
            "여가": ["영화", "전시회", "게임"],
            "교육": ["학원", "온라인강의"],
            "외식·숙박": ["외식", "배달음식", "숙박"],
            "기타": ["기부", "보험료", "잡화/기타"],
        }

        self.stdout.write("📁 최상위 카테고리 생성 중...")

        parent_map = {}  # name -> Category 객체 저장용
        for parent_name in categories_data.keys():
            parent, created = Category.objects.get_or_create(
                name=parent_name, parent_category=None
            )
            parent_map[parent_name] = parent
            if created:
                self.stdout.write(f"  • 최상위 카테고리 '{parent.name}' 생성")

        self.stdout.write("📁 서브카테고리 생성 중...")

        for parent_name, child_names in categories_data.items():
            parent = parent_map[parent_name]

            existing_children = set(
                Category.objects.filter(parent_category=parent).values_list(
                    "name", flat=True
                )
            )

            new_children = [
                Category(name=child_name, parent_category=parent)
                for child_name in child_names
                if child_name not in existing_children
            ]

            Category.objects.bulk_create(new_children)
            self.stdout.write(
                f"    └─ '{parent.name}'에 서브카테고리 {len(new_children)}개 생성 완료"
            )

        self.stdout.write(self.style.SUCCESS("✅   모든 카테고리 생성 완료"))
