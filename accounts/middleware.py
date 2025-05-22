from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.response import Response
from rest_framework import status
from .utils import response

class TokenBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Authorization 헤더가 있는 경우에만 체크
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # 토큰이 블랙리스트에 있는지 확인
                outstanding_token = OutstandingToken.objects.get(token=token)
                if BlacklistedToken.objects.filter(token=outstanding_token).exists():
                    return response.error(
                        message='이미 로그아웃된 토큰입니다.',
                        code=status.HTTP_401_UNAUTHORIZED
                    )
            except OutstandingToken.DoesNotExist:
                pass

        return self.get_response(request)