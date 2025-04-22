from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.kakao import views as kakao_views
from allauth.socialaccount.providers.naver import views as naver_views

@login_required # 로그인 된 사용자만 접근 가능하도록
def social_login_redirect(request):
    # 프론트엔드 서버의 기본 URL 또는 특정 콜백 URL 설정
    # 이 부분을 실제 프론트엔드 주소로 변경하세요.
    frontend_url = 'http://localhost:3000/' 

    # 필요하다면, 사용자 정보나 토큰 등을 쿼리 파라미터로 전달할 수 있습니다.
    # 예: JWT 토큰을 생성하여 전달하는 경우 (Simple JWT 사용 시)
    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)
    # frontend_url = f'http://localhost:3000/auth/callback?token={access_token}'
    frontend_url = f'http://localhost:3000/auth/callback?token={access_token}'

    # 최종적으로 프론트엔드 URL로 리디렉션
    return HttpResponseRedirect(frontend_url)
