from rest_framework import serializers
from .models import Challenge, UserChallenge

# 챌린지 전체 목록 조회
class ChallengeListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    computed_status = serializers.CharField(read_only=True)

    class Meta:
        model = Challenge
        fields = [
            'challenge_id',
            'title',
            'content',
            'goal_amount',
            'goal_days',
            'point',
            'start_date',
            'end_date',
            'category',
            'category_name',
            'is_active',
            'computed_status',
        ]


# 챌린지 상세 조회
class ChallengeDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    computed_status = serializers.CharField(read_only=True)
    challenge_host_company = serializers.CharField(source='challenge_host.company_name', read_only=True)

    class Meta:
        model = Challenge
        fields = [
            'challenge_id',
            'title',
            'content',
            'goal_amount',
            'goal_days',
            'point',
            'start_date',
            'end_date',
            'category',
            'category_name',
            'is_active',
            'challenge_host',
            'challenge_host_company',
            'computed_status',
        ]


# 도전중, 성공, 실패한 챌린지 목록
class ChallengeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['challenge_id', 'title', 'goal_amount', 'point']

class UserChallengeListSerializer(serializers.ModelSerializer):
    challenge = ChallengeShortSerializer(read_only=True)
    computed_progress = serializers.SerializerMethodField()

    class Meta:
        model = UserChallenge
        fields = [
            'user_challenge_id',
            'challenge',
            'status',
            'target_expense',
            'previous_expense',
            'total_expense',
            'progress',
            'computed_progress',
        ]

    def get_computed_progress(self, obj):
        return obj.computed_progress

class ChallengeSummarySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    challenge_host_company = serializers.CharField(source='challenge_host.company_name', read_only=True)

    class Meta:
        model = Challenge
        fields = [
            'challenge_id',
            'title',
            'content',
            'goal_amount',
            'goal_days',
            'point',
            'start_date',
            'end_date',
            'is_active',
            'category',
            'category_name',
            'challenge_host',
            'challenge_host_company',
            'computed_status',
        ]

class UserChallengeDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    challenge = ChallengeSummarySerializer(read_only=True)
    computed_progress = serializers.SerializerMethodField()

    class Meta:
        model = UserChallenge
        fields = [
            'user_challenge_id',
            'user_id',
            'challenge',
            'status',
            'target_expense',
            'previous_expense',
            'total_expense',
            'progress',
            'computed_progress',
            'start_date',
            'end_date',
            'created_at',
            'updated_at',
        ]

    def get_computed_progress(self, obj):
        return obj.computed_progress