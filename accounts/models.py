from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _ # 번역 지원 추가

# Create your models here.
class User(AbstractUser):
    # AbstractUser의 email 필드를 unique=True로 오버라이드
    email = models.EmailField(_("email address"), unique=True)

    # 0: 일반 사용자, 1: 주최자, 2: 관리자
    user_role = models.IntegerField(default=0)
    # user_password = password 필드 사용 (해싱 포함)
    # user_email = email 필드 사용
    user_nickname = models.CharField(max_length=50)
    # 0: 비활성화 1: 활성화, 2: 탈퇴
    user_status = models.IntegerField(default=1)
    # user_created_at = date_joined 필드 사용 가능
    user_changed_at = models.DateTimeField(auto_now=True) # AbstractUser의 last_login과 유사하지만, 모델 변경 시마다 갱신

    # AbstractUser의 기본 필드를 사용하도록 변경
    USERNAME_FIELD = 'email'
    # email은 USERNAME_FIELD이므로 REQUIRED_FIELDS에 포함될 필요 없음
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_nickname']
    EMAIL_FIELD = 'email'   
    
    def __str__(self):
        return self.get_full_name() or self.email

class UserProfile(models.Model):
    user_info_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_level = models.IntegerField(default=1)
    user_exp = models.IntegerField(default=0)
    user_mileage = models.IntegerField(default=0)
    user_average_income = models.FloatField(default=0)
