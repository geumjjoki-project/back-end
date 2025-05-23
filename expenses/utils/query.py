from rest_framework.exceptions import ValidationError
from django.db.models import Q

def get_ordering(field: str, direction: str = "desc"):
    if direction not in ["asc", "desc"]:
        raise ValidationError({
            "INVALID_ORDER": "정렬 기준은 asc 또는 desc만 허용됩니다",
        })
    return f"-{field}" if direction == "desc" else field


def get_category_filter_q(category_list):
    q = Q()
    for cat in category_list:
        q |= Q(category__name__icontains=cat) | Q(category__parent_category__name__icontains=cat)
    return q
