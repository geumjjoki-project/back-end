from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # allauth URL은 그대로 유지
    # 직접 카카오 로그인 시작 URL
    path('kakao-login/', views.kakao_login, name='kakao_login'),
    # 소셜 로그인 성공 후 콜백 URL
    path('login/callback/', views.social_login_callback, name='login_callback'),
    path('email-login/', views.email_login, name='email_login'),
    path('email-signup/', views.email_signup, name='email_signup'),
    path('logout/', views.logout, name='logout'),
    path('user/', views.get_user, name='get_user'),
]