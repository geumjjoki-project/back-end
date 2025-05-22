from rest_framework.response import Response
from rest_framework import status
def success_response(data: dict, status_code=status.HTTP_200_OK):
    return Response({
        "status": "success",
        "data": data,
    }, status=status_code)


def error_response(message: str, error_code: str = "ERROR", status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "status": "error",
        "message": message,
        "error_code": error_code,
    }, status=status_code)
