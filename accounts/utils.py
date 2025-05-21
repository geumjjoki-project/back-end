from rest_framework.response import Response
from rest_framework import status

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
