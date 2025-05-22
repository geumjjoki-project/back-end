from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _  # 번역 지원 추가


# Create your models here.


# 회원
class User(AbstractUser):
    ##################################################
    # 역할
    # 0: 일반 사용자, 1: 주최자, 2: 관리자
    role = models.IntegerField(
        default=0,
    )
    # username = 회원명
    # password = 비밀번호
    # AbstractUser의 email 필드를 unique=True로 오버라이드
    email = models.EmailField(
        _("email address"),
        unique=True,
    )
    # 프로필사진
    profile_image = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True,
    )
    # 별명
    nickname = models.CharField(
        max_length=50,
        null=True,
    )
    # 회원상태
    # 0: 비활성화 1: 활성화, 2: 탈퇴
    status = models.IntegerField(
        default=1,
    )
    # 계정변경일시
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    ##################################################
    # AbstractUser의 기본 필드를 사용하도록 변경
    USERNAME_FIELD = "email"
    # email은 USERNAME_FIELD이므로 REQUIRED_FIELDS에 포함될 필요 없음
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]
    EMAIL_FIELD = "email"

    def __str__(self):
        return self.get_full_name() or self.email


# 회원프로필
class UserProfile(models.Model):
    ##################################################
    # 회원프로필식별자
    user_profile_id = models.AutoField(
        primary_key=True,
    )
    # 회원식별자
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_profile",
    )
    # 레벨
    level = models.IntegerField(
        default=1,
    )
    # 경험치
    exp = models.IntegerField(
        default=0,
    )
    # 마일리지
    point = models.IntegerField(
        default=0,
    )
    # 평균수입
    average_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    ##################################################
