from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from django.contrib.auth import authenticate, login, logout as auth_logout
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('accounts')

@csrf_exempt
@api_view(['POST'])
def email_login(request):
    """이메일 로그인 기능, JWT 토큰 발급"""
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return redirect(f'http://localhost:5173/auth/email/callback?token={access_token}')
    else:
        return redirect('http://localhost:5173/login', {'error': 'Invalid credentials'})

@csrf_exempt
@api_view(['POST'])
def email_signup(request):
    """이메일 회원가입 기능"""
    User = get_user_model()
    email = request.POST.get('email')
    password = request.POST.get('password')
    username = request.POST.get('username')
    password_confirm = request.POST.get('password_confirm')
    if password != password_confirm:
        return redirect('http://localhost:5173/auth/signup', {'error': '비밀번호가 일치하지 않습니다.'})
    user = User.objects.create_user(email=email, password=password, username=username)
    login(request, user)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    return redirect(f'http://localhost:5173/auth/email/callback?token={access_token}')

@csrf_exempt
def kakao_login(request):
    """사용자를 카카오 로그인 페이지로 리디렉션"""
    return redirect('/accounts/kakao/login/')

@csrf_exempt
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

@csrf_exempt
@api_view(['POST'])
@login_required
def logout(request):
    """로그아웃 기능 jwt 토큰 삭제"""
    try:
        # Django 세션에서 로그아웃
        auth_logout(request)
        
        # 프론트엔드로 리디렉션
        return redirect('http://localhost:5173/')
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        return redirect('http://localhost:5173/')
