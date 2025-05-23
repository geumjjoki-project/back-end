from django.db import models
from django.conf import settings


# 리워드
class Reward(models.Model):
    ##################################################
    # 리워드식별자
    reward_id = models.BigAutoField(
        primary_key=True,
    )
    # 이름
    name = models.CharField(max_length=50)
    # 설명
    description = models.CharField(max_length=255)
    # 비용
    point = models.IntegerField()
    # 유효기간
    valid_days = models.IntegerField()
    # 활성화여부
    is_active = models.BooleanField()
    # 카테고리
    category = models.CharField(
        max_length=50,
        default='기타',
    )
    ##################################################


# 리워드이미지
class RewardImage(models.Model):
    ##################################################
    # 리워드이미지식별자
    reward_image_id = models.BigAutoField(
        primary_key=True,
    )
    # 리워드식별자
    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
        related_name="images",
    )
    # 이미지
    image = models.ImageField(
        upload_to="reward_images/",
    )
    # 업로드일시
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )
    ##################################################


# 리워드교환목록
class RewardTransaction(models.Model):
    ##################################################
    # 리워드교환목록식별자
    reward_transaction_id = models.BigAutoField(
        primary_key=True,
    )
    # 회원식별자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 리워드식별자
    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
    )
    # 교환상태
    # 0: 이용가능, 1: 사용완료, 2: 만료, 3: 중지
    status = models.IntegerField(
        default=0,
    )
    # 교환일시
    redeemed_at = models.DateTimeField(auto_now_add=True)
    # 만료일시
    expire_at = models.DateTimeField()
    ##################################################
