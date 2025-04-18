from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ... 다른 accounts 관련 URL 패턴들 ...
    path('social/redirect/', views.social_login_redirect, name='social_login_redirect'),
] 