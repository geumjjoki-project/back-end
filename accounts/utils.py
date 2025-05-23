from rest_framework.response import Response
from rest_framework import status
import re

class AccountsResponse:
    def ok(self, message="요청 성공", data=None, code=status.HTTP_200_OK):
        response = {
            'status': 'success',
            'message': message,
            'data': data,
            'code': code,
        }
        return Response(response, status=code)
    
    def error(self, message, code=status.HTTP_400_BAD_REQUEST):
        response = {
            'status': 'error',
            'message': message,
            'code': code,
        }
        return Response(response, status=code)

response = AccountsResponse()

# 이메일 형식 체크
def is_valid_email(email):
    if not email:
        return False
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    return True


# 비밀번호 형식 체크
# 문자, 숫자, 특수문자 포함 8~20자
def is_valid_password(password):
    if not password:
        return False
    # 문자, 숫자, 특수문자 포함
    if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+-=[]{}|;:,.<>?]+$', password):
        return False
    # 8~20자
    if len(password) < 8 or len(password) > 20:
        return False
    return True
