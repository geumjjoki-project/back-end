from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from django.contrib.auth import authenticate, login, logout as auth_logout
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile


logger = logging.getLogger('accounts')

@api_view(['GET'])
def email_duplicate_check(request):
    # 이메일 중복 체크 기능
    email = request.GET.get('email')
    User = get_user_model()
    user = User.objects.filter(email=email)
    if user:
        return Response({
            'duplication': True
        })
    else:
        return Response({
            'duplication': False
        })
        

@csrf_exempt
@api_view(['POST'])
def email_login(request):
    """이메일 로그인 기능, JWT 토큰 발급"""
    User = get_user_model()
    email = request.data.get('email')
    password = request.data.get('password')
    # 먼저 이메일로 사용자가 존재하는지 확인
    try:
        user = User.objects.get(email=email)
        # 기존 사용자 인증
        user = authenticate(request, email=email, password=password)
        if user is None:
            return redirect('http://localhost:5173/auth/login', {'error': '비밀번호가 일치하지 않습니다'})
    except User.DoesNotExist:
        # 새 사용자 생성
        user = User.objects.create_user(email=email, password=password, username=email)
        # 프로필 생성
        UserProfile.objects.create(
            user=user,
            level=1,
            exp=0,
            mileage=0,
            average_income=0.00
        )
    login(request, user)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    return Response({
        'token': access_token
    })
    # return redirect(f'http://localhost:5173/auth/callback?token={access_token}')

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
    return redirect(f'http://localhost:5173/auth/callback?token={access_token}')


@api_view(['GET'])
def kakao_login(request):
    """사용자를 카카오 로그인 페이지로 리디렉션"""
    # allauth 자동 지정 로그인 페이지
    return redirect('/accounts/kakao/login/')
    # 로그인 완료시 자동으로 allauth 에서 지정한 http://localhost:8000/accounts/kakao/login/callback/ 페이지로 리디렉션
    # adapter.py 실행 후 settings.py 에 지정한 LOGIN_REDIRECT_URL로 리디렉션

@csrf_exempt
def social_login_callback(request):
    """
    소셜 로그인 성공 후 JWT 토큰을 생성하여 프론트엔드로 리디렉션
    """
    try:
        # 사용자가 인증되었다면 JWT 토큰 생성
        if not request.user.is_authenticated:
            logger.error("User is not authenticated")
            return HttpResponseRedirect('http://localhost:5173/auth/login')
            
        # 사용자 정보 로깅
        logger.debug(f"Authenticated user: {request.user.email}, ID: {request.user.id}")
        
        # JWT 토큰 생성
        refresh = RefreshToken.for_user(request.user)
        access_token = str(refresh.access_token)
        
        # 토큰 생성 확인을 위한 로깅
        logger.debug(f"Generated token for user: {request.user.email}")
        
        # 프론트엔드로 토큰과 함께 리디렉션
        frontend_url = f'http://localhost:5173/auth/callback?token={access_token}'
        logger.debug(f"Redirecting to frontend with token: {frontend_url}")
        return HttpResponseRedirect(frontend_url)
    
    except Exception as e:
        logger.error(f"Error in social_login_callback: {str(e)}")
        # # 상세한 에러 정보 로깅
        import traceback
        logger.error(traceback.format_exc())
        return HttpResponseRedirect('http://localhost:5173/auth/login', {'error': '로그인 실패'})

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """로그아웃 기능 jwt 토큰 삭제"""
    try:
        # Django 세션에서 로그아웃
        auth_logout(request)
        # 프론트엔드로 리디렉션
        return redirect('http://localhost:5173/auth/login')
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        return redirect('http://localhost:5173/auth/login')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    """사용자 정보 조회"""
    try:
        # # 요청 헤더 로깅
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Authorization header: {request.headers.get('Authorization')}")
        
        # 인증된 사용자 정보 로깅
        logger.debug(f"Authenticated user: {request.user}")
        logger.debug(f"User ID: {request.user.id}")
        
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({"error": str(e)}, status=500)