from django.db import models
from django.conf import settings
from challenges.models import UserChallenge


# Create your models here.
# 카테고리
class Category(models.Model):
    ##################################################
    # 카테고리식별자
    category_id = models.BigAutoField(
        primary_key=True,
    )
    # 상위카테고리식별자
    parent_category = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="child_category",
        on_delete=models.CASCADE,
    )
    # 이름
    name = models.CharField(max_length=100)
    ##################################################

    # 카테고리의 이름을 표시
    def __str__(self):
        return self.name

    # 최상위 카테고리를 반환
    def get_root_category(self):
        if self.parent_category:
            return self.parent_category.get_root_category()
        return self


# 지출내역
class Expense(models.Model):
    ##################################################
    # 지출내역식별자
    expense_id = models.BigAutoField(
        primary_key=True,
    )
    # 회원식별자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense",
    )
    # 카테고리식별자
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # 지출내용
    description = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    # 지출금액
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    # 지출일자
    date = models.DateField()

    # 나의챌린지식별자
    user_challenge_id = models.ForeignKey(
        UserChallenge,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expense",
    )
    ##################################################

    @property
    # 최상위 카테고리를 반환
    def root_category(self):
        if self.category:
            try:
                return self.category.get_root_category()
            except Exception:
                pass
        # 카테고리가 존재하지 않으면 기타 카테고리를 반환함
        try:
            return Category.objects.get(pk=7)  # 기타 카테고리의 pk 지정
        except Category.DoesNotExist:
            return None


# 지출내역분석
class ExpenseAnalysis(models.Model):
    ##################################################
    # 지출내역분석식별자
    expense_analysis_id = models.BigAutoField(
        primary_key=True,
    )
    # 회원식별자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 제목
    title = models.CharField(
        max_length=100,
    )
    # 내용
    content = models.TextField()
    ##################################################
