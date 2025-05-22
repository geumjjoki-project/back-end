from rest_framework import serializers
from .models import RewardTransaction, Reward, RewardImage


# 리워드이미지
class RewardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardImage
        fields = ("image",)


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = "__all__"


class RewardListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Reward
        fields = (
            "reward_id",
            "name",
            "description",
            "point",
            "thumbnail",
            "category",
        )

    def get_thumbnail(self, obj):
        try:
            first_image = obj.images.first()
            return first_image.image.url if first_image and first_image.image else None
        except Exception:
            return None


# 전체리워드
class RewardSerializer(serializers.ModelSerializer):
    images = RewardImageSerializer(many=True, read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Reward
        fields = (
            "reward_id",
            "name",
            "description",
            "thumbnail",
            "images",
            "point",
            "valid_days",
            "is_active",
            "category",
        )

    def get_thumbnail(self, obj):
        try:
            first_image = obj.images.first()
            return first_image.image.url if first_image and first_image.image else None
        except Exception:
            return None


# 교환한 리워드 전체 조회
class RewardTransactionSerializer(serializers.ModelSerializer):
    class RewardSerializerForRewardTransaction(serializers.ModelSerializer):
        images = RewardImageSerializer(many=True, read_only=True)
        thumbnail = serializers.SerializerMethodField()

        def get_thumbnail(self, obj):
            try:
                first_image = obj.images.first()
                return (
                    first_image.image.url if first_image and first_image.image else None
                )
            except Exception:
                return None

        class Meta:
            model = Reward
            fields = (
                "reward_id",
                "name",
                "description",
                "thumbnail",
                "images",
                "point",
                "category",
            )

    reward = RewardSerializerForRewardTransaction(read_only=True)

    class Meta:
        model = RewardTransaction
        fields = (
            "reward_transaction_id",
            "status",
            "reward",
            "redeemed_at",
            "expire_at",
        )
