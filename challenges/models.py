from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now

# Create your models here.

STATUS_CHOICES = [
    ("도전중", "도전중"),
    ("성공", "성공"),
    ("실패", "실패"),
]

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
    # 목표 지출
    goal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    # 카테고리
    category = models.ForeignKey("expenses.Category", on_delete=models.SET_NULL, null=True, blank=True, related_name="challenges")
    # 보상 마일리지
    point = models.PositiveIntegerField()
    # 목표 기간
    goal_days = models.PositiveIntegerField()
    # 시작일
    start_date = models.DateTimeField()
    # 종료일
    end_date = models.DateTimeField()
    # 활성화 여부
    is_active = models.BooleanField(default=True)
    # 생성일
    created_at = models.DateTimeField(auto_now_add=True)
    # 수정일
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def computed_status(self):
        today = now().date()
        start = self.start_date.date()
        end = self.end_date.date()
        remaining_days = (end - today).days

        if today < start:
            return "예정"
        elif today > end:
            return "종료"
        elif remaining_days < self.goal_days:
            return "도전불가"
        return "도전가능"

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
    # 시작일
    start_date = models.DateTimeField()
    # 종료일
    end_date = models.DateTimeField()
    # 진행도
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    # 상태
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="도전중"
    )
    
    # 기록용
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def computed_progress(self):
        if self.previous_expense == 0:
            return 0
        saved = self.previous_expense - self.total_expense
        return max(0, round((saved / self.previous_expense) * 100, 2))
    
    @classmethod
    def create_for_user(cls, user, challenge, **kwargs):
        now = timezone.now()
        start_date = now
        end_date = start_date + timedelta(days=challenge.goal_days)
        return cls.objects.create(
            user=user,
            challenge=challenge,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
