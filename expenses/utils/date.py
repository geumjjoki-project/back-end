from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError

def validate_and_parse_dates(start_date, end_date):
    parsed_start = parse_date(start_date) if start_date else None
    parsed_end = parse_date(end_date) if end_date else None

    if start_date and not parsed_start:
        raise ValidationError({
            "INVALID_START_DATE": "시작일 형식이 잘못되었습니다",
        })

    if end_date and not parsed_end:
        raise ValidationError({
            "INVALID_END_DATE": "종료일 형식이 잘못되었습니다",
        })

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise ValidationError({
            "INVALID_DATE_RANGE": "시작일은 종료일보다 이전이어야 합니다",
        })

    return parsed_start, parsed_end
