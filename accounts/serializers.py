# user serializer

from rest_framework import serializers
from .models import User, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class UserProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = UserProfile
            fields = ['level', 'exp', 'mileage', 'average_income']

    user_profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'role', 'nickname', 'status', 'user_profile']
