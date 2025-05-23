from rest_framework.response import Response

def success_response(data={}, message="요청에 성공했습니다.", code=200):
    return Response({
        "status": "success",
        "message": message,
        "code": code,
        "data": data
    }, status=code)

def error_response(message, error_code=None, code=400):
    resp = {
        "status": "error",
        "code": code,
        "message": message,
    }
    if error_code:
        resp["error_code"] = error_code
    return Response(resp, status=code)