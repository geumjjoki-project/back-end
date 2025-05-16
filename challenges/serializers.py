from rest_framework import serializers
from .models import Challenge, UserChallenge

# 챌린지 전체 목록 조회
class ChallengeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            'challenge_id',
            'title',
            'start_date',
            'end_date',
            'status',
        ]


# 챌린지 상세 조회
class ChallengeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            'challenge_id',
            'title',
            'content',
            'start_date',
            'end_date',
            'status'
        ]


# 진행, 성공, 실패한 챌린지 목록
class UserChallengeListSerializer(serializers.ModelSerializer):
    challenge_id = serializers.IntegerField(source='challenge.challenge_id')
    title = serializers.CharField(source='challenge.title')
    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        model = UserChallenge
        fields = [
            'user_challenge_id',
            'user_id',
            'challenge_id',
            'title',
            'status',
            'target_expense',
            'previous_expense',
            'total_expense',
            'progress',
        ]