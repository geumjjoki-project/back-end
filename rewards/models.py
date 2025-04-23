from django.db import models
from django.conf import settings

# Create your models here.


# 리워드
class Reward(models.Model):
    ##################################################
    # 리워드식별자
    reward_id = models.BigAutoField(
        primary_key=True,
    )
    # 리워드이름
    name = models.CharField(max_length=50)
    # 리워드비용
    cost = models.IntegerField()
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
    # 0: 진행중, 1: 완료, 2: 중지
    is_changed = models.IntegerField(
        default=0,
    )
    ##################################################
