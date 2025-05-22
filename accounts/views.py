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
from rest_framework import status
from .utils import response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

logger = logging.getLogger('accounts')

@api_view(['GET'])
def email_duplicate_check(request):
    # 이메일 중복 체크 기능
    email = request.GET.get('email')
    User = get_user_model()
    user = User.objects.filter(email=email)
    if user:
        return response.ok(
            data={'duplication': True}
        )
    else:
        return response.ok(
            data={'duplication': False}
        )
        

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
            return response.error(
                message='비밀번호가 일치하지 않습니다.',
                code=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        # 새 사용자 생성
        user = User.objects.create_user(email=email, password=password, username=email)
        # 프로필 생성
        UserProfile.objects.create(
            user=user,
            level=1,
            exp=0,
            point=0,
            average_income=0.00
        )
    login(request, user)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    return Response({
        'access_token': access_token,
        'refresh_token': refresh_token
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
        return response.error(
            message='비밀번호가 일치하지 않습니다.',
            code=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.create_user(email=email, password=password, username=username)
    UserProfile.objects.create(
        user=user,
        level=1,
        exp=0,
        point=0,
        average_income=0.00
    )
    login(request, user)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    return response.ok(
        data={
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    )


@api_view(['GET'])
def kakao_login(request):
    """사용자를 카카오 로그인 페이지로 리디렉션"""
    # allauth 자동 지정 로그인 페이지
    return redirect('/accounts/kakao/login/')
    # 로그인 완료시 자동으로 allauth 에서 지정한 http://localhost:8000/accounts/kakao/login/callback/ 페이지로 리디렉션
    # adapter.py 실행 후 settings.py 에 지정한 LOGIN_REDIRECT_URL로 리디렉션

@api_view(['GET'])
def naver_login(request):
    """사용자를 네이버 로그인 페이지로 리디렉션"""
    # allauth 자동 지정 로그인 페이지
    return redirect('/accounts/naver/login/')

@csrf_exempt
def social_login_callback(request):
    """
    소셜 로그인 성공 후 JWT 토큰을 생성하여 프론트엔드로 리디렉션
    """
    try:
        # 사용자가 인증되었다면 JWT 토큰 생성
        if not request.user.is_authenticated:
            error_message = "인증 되지 않은 사용자 입니다."
            logger.error(error_message)
            return HttpResponseRedirect(f'http://localhost:5173/auth/login?error={error_message}')
            
        # 사용자 정보 로깅
        logger.debug(f"Authenticated user: {request.user.email}, ID: {request.user.id}")
        
        # JWT 토큰 생성
        refresh = RefreshToken.for_user(request.user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        # 토큰 생성 확인을 위한 로깅
        logger.debug(f"Generated token for user: {request.user.email}")
        
        # 프론트엔드로 토큰과 함께 리디렉션
        frontend_url = f'http://localhost:5173/auth/callback?access_token={access_token}&refresh_token={refresh_token}'
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
def logout(request):
    """로그아웃 기능 jwt 토큰 삭제"""
    try:
        # Django 세션 로그아웃 추가
        auth_logout(request)
        
        # 현재 사용자의 refresh 토큰을 블랙리스트에 추가
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return response.ok(
            message='로그아웃 성공',
            code=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        return response.error(
            message='로그아웃 실패',
            code=status.HTTP_400_BAD_REQUEST
        )

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
        return response.ok(
            data=serializer.data
        )
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return response.error(
            message=str(e),
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return response.error(
            message='refresh 토큰이 제공되지 않았습니다.',
            code=status.HTTP_400_BAD_REQUEST
        )
    try:
        token = RefreshToken(refresh_token)
        jti = token['jti']
        try:
            outstanding_token = OutstandingToken.objects.get(jti=jti)
            # 블랙리스트 여부는 BlacklistedToken에서 확인!
            if BlacklistedToken.objects.filter(token=outstanding_token).exists():
                return response.error(
                    message='유효하지 않은 refresh 토큰입니다.',
                    code=status.HTTP_401_UNAUTHORIZED
                )
        except OutstandingToken.DoesNotExist:
            return response.error(
                message='존재하지 않는 refresh 토큰입니다.',
                code=status.HTTP_401_UNAUTHORIZED
            )
        access_token = str(token.access_token)
        return response.ok(
            data={
                'access_token': access_token
            }
        )
    except Exception as e:
        logger.error(f"Error in refresh_token: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return response.error(
            message=str(e),
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )