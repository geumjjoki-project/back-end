from django.db import models
from django.conf import settings

# Create your models here.
class ChallengeHost(models.Model):
    challenge_host_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge_host_company_name = models.TextField()
    challenge_host_phone_number = models.TextField()

class Challenge(models.Model):
    challenge_id = models.AutoField(primary_key=True)
    challenge_host = models.ForeignKey(ChallengeHost, on_delete=models.CASCADE)
    challenge_title = models.CharField(max_length=100)
    challenge_content = models.TextField()
    challenge_target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    challenge_status = models.CharField(max_length=20)
    challenge_start_date = models.DateTimeField()
    challenge_end_date = models.DateTimeField()

class UserChallenge(models.Model):
    user_challenge_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    user_challenge_total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user_challenge_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    user_challenge_status = models.CharField(max_length=20)
