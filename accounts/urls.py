from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # allauth URL은 그대로 유지
    # 직접 카카오 로그인 시작 URL
    path('kakao-login/', views.kakao_login, name='kakao_login'), # GET
    path('naver-login/', views.naver_login, name='naver_login'), # GET
    # 소셜 로그인 성공 후 콜백 URL
    path('login/callback/', views.social_login_callback, name='login_callback'), # GET
    path('email-login/', views.email_login, name='email_login'), # POST
    path('email-signup/', views.email_signup, name='email_signup'), # POST
    path('logout/', views.logout, name='logout'), # POST
    path('user/', views.UserInfoView.as_view(), name='user_info'), # GET, PUT, DELETE
    path('user/change-password/', views.change_password, name='change_password'), # PUT
    path('email-check/', views.email_duplicate_check, name='email_duplicate_check'), # GET
    path('token/refresh/', views.refresh_token, name='refresh_token') # POST
]