from django.db import models
from django.conf import settings

# Create your models here.


# 챌린지주최자
class ChallengeHost(models.Model):
    # 챌린지주최자식별자
    challenge_host_id = models.BigAutoField(
        primary_key=True,
    )
    # 회원식별자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 회사명
    company_name = models.TextField()
    # 전화번호
    phone_number = models.TextField()


# 챌린지
class Challenge(models.Model):
    # 챌린지식별자
    challenge_id = models.BigAutoField(
        primary_key=True,
    )
    # 챌린지주최자식별자
    challenge_host = models.ForeignKey(
        ChallengeHost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # 제목
    title = models.CharField(
        max_length=100,
    )
    # 내용
    content = models.TextField()
    # 카테고리
    category = models.ForeignKey("expenses.Category", on_delete=models.SET_NULL, null=True, blank=True, related_name="challenges")
    # 보상 마일리지
    point = models.PositiveIntegerField()
    # 상태: 진행중, 예정, 종료, 중지
    status = models.CharField(
        max_length=20,
        default="예정",
    )
    # 목표 기간
    goal_days = models.PositiveIntegerField()
    # 시작일
    start_date = models.DateTimeField()
    # 종료일
    end_date = models.DateTimeField()


# 나의챌린지
class UserChallenge(models.Model):
    # 나의챌린지식별자
    user_challenge_id = models.BigAutoField(primary_key=True)
    # 회원식별자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 챌린지식별자
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
    )
    # 목표금액
    target_expense = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    # 이전지출금액
    previous_expense = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    # 누적지출금액
    total_expense = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    # 진행도
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    # 상태
    status = models.CharField(
        max_length=20,
    )
