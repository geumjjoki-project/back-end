from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger('accounts')

def kakao_login(request):
    """사용자를 카카오 로그인 페이지로 리디렉션"""
    return redirect('/accounts/kakao/login/')

@login_required
def social_login_callback(request):
    """
    소셜 로그인 성공 후 JWT 토큰을 생성하여 프론트엔드로 리디렉션
    """
    try:
        # 사용자가 인증되었다면 JWT 토큰 생성
        refresh = RefreshToken.for_user(request.user)
        access_token = str(refresh.access_token)
        
        # 프론트엔드로 토큰과 함께 리디렉션 (프론트엔드 라우터에 맞게 경로 수정)
        frontend_url = f'http://localhost:5173/auth/kakao/callback?token={access_token}'
        logger.debug(f"Redirecting to frontend with token: {frontend_url}")
        return HttpResponseRedirect(frontend_url)
    except Exception as e:
        logger.error(f"Error in social_login_callback: {e}")
        # 오류 발생 시 프론트엔드 메인으로 리디렉션
        return HttpResponseRedirect('http://localhost:5173/')