from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException


def custom_exception_handler(exc, context):
    # 1. DRF 기본 처리 먼저 실행
    response = drf_exception_handler(exc, context)

    # 2. DRF가 이미 에러로 처리한 경우
    if response is not None:
        # 기본 status_code는 그대로 유지
        status_code = response.status_code

        # 기본 메시지 추출 (dict일 수도 있고 list일 수도 있음)
        if isinstance(response.data, dict):
            # ValidationError의 경우 field 단위 메시지가 dict로 올 수 있음
            message = list(response.data.values())[0]
            if isinstance(message, list):
                message = message[0]
            error_code = list(response.data.keys())[0].upper()
        else:
            # 기타 예외는 str
            message = str(response.data)
            error_code = "UNKNOWN_ERROR"

        return Response(
            {
                "status": "error",
                "message": message,
                "error_code": error_code,
            },
            status=status_code,
        )

    # 3. DRF가 처리하지 못한 에러 (예: 코드 오류 등)
    return Response(
        {
            "status": "error",
            "message": str(exc),
            "error_code": "INTERNAL_SERVER_ERROR",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
