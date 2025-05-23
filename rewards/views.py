from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.db.models import Q
from accounts.models import UserProfile
from django.utils import timezone
from datetime import timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rewards.utils.response import success_response, error_response
from .models import Reward, RewardTransaction
from .serializers import (
    RewardListSerializer,
    RewardTransactionSerializer,
    RewardSerializer,
)
from .pagination import CustomRewardPagination

class RewardBaseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class RewardListView(RewardBaseView):
    def get(self, request):
        is_active = request.query_params.get("is_active")
        search = request.query_params.get("search")
        min_point = request.query_params.get("min_point")
        max_point = request.query_params.get("max_point")
        ordering = request.query_params.get("ordering")
        DEFAULT_ORDERING = ["-is_active", "point"]

        rewards = Reward.objects.all()

        if is_active is not None:
            if is_active.lower() == "true":
                rewards = rewards.filter(is_active=True)
            elif is_active.lower() == "false":
                rewards = rewards.filter(is_active=False)
            else:
                return error_response("is_active는 true 또는 false여야 합니다.", "INVALID_IS_ACTIVE_PARAM")

        if search:
            rewards = rewards.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        try:
            if min_point is not None:
                rewards = rewards.filter(point__gte=int(min_point))
            if max_point is not None:
                rewards = rewards.filter(point__lte=int(max_point))
        except ValueError:
            return error_response("min_point 및 max_point는 정수여야 합니다.", "INVALID_POINT_PARAM")

        if ordering:
            fields = [f.strip() for f in ordering.split(",") if f.strip()]
            try:
                rewards = rewards.order_by(*fields)
            except:
                rewards = rewards.order_by(*DEFAULT_ORDERING)
        else:
            rewards = rewards.order_by(*DEFAULT_ORDERING)

        paginator = CustomRewardPagination()
        paginated = paginator.paginate_queryset(rewards, request)
        serializer = RewardListSerializer(paginated, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data).data
        return success_response(paginated_data)

class RewardDetailView(RewardBaseView):
    def get(self, request, reward_id):
        reward = get_object_or_404(Reward, reward_id=reward_id)
        serializer = RewardSerializer(reward)
        return success_response(serializer.data)

class RewardTransactionListView(RewardBaseView):
    def get(self, request):
        status_param = request.query_params.get("status")
        search = request.query_params.get("search")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        ordering = request.query_params.get("ordering", "-redeemed_at")

        transactions = RewardTransaction.objects.select_related("reward").filter(
            user=request.user
        )

        if status_param is not None:
            try:
                status_filter = int(status_param)
                transactions = transactions.filter(status=status_filter)
            except ValueError:
                return error_response("status는 정수여야 합니다.", "INVALID_STATUS_PARAM")

        if start_date:
            parsed_start = parse_date(start_date)
            if not parsed_start:
                return error_response("start_date는 YYYY-MM-DD 형식이어야 합니다.", "INVALID_START_DATE")
            transactions = transactions.filter(redeemed_at__date__gte=parsed_start)

        if end_date:
            parsed_end = parse_date(end_date)
            if not parsed_end:
                return error_response("end_date는 YYYY-MM-DD 형식이어야 합니다.", "INVALID_END_DATE")
            transactions = transactions.filter(redeemed_at__date__lte=parsed_end)

        if search:
            transactions = transactions.filter(
                Q(reward__name__icontains=search) | Q(reward__description__icontains=search)
            )

        valid_ordering_fields = [
            "redeemed_at",
            "-redeemed_at",
            "expire_at",
            "-expire_at",
        ]
        if ordering not in valid_ordering_fields:
            return error_response("허용되지 않은 정렬 기준입니다.", "INVALID_ORDERING_PARAM")

        transactions = transactions.order_by(ordering)

        paginator = CustomRewardPagination()
        paginated = paginator.paginate_queryset(transactions, request)
        serializer = RewardTransactionSerializer(paginated, many=True)
        return success_response(paginator.get_paginated_response(serializer.data).data)

class RewardTransactionDetailView(RewardBaseView):
    def get(self, request, reward_transaction_id):
        transaction = RewardTransaction.objects.select_related("reward").get(
            pk=reward_transaction_id
        )
        
        if transaction.user != request.user:
            return error_response("본인의 교환내역만 조회할 수 있습니다.", "REWARD_TRANSACTION_PERMISSION_DENIED")

        serializer = RewardTransactionSerializer(transaction)
        return success_response(serializer.data)


class RewardTransactionCreateView(RewardBaseView):
    def post(self, request):
        try:
            reward_id = request.GET.get("reward_id")
            reward = Reward.objects.get(reward_id=reward_id)
            user = request.user
            userProfile = UserProfile.objects.get(user=user)
            
            if reward.is_active == False:
                return error_response("활성화되지 않은 리워드입니다.")
            if userProfile.point < reward.point:
                return error_response(f"포인트가 {reward.point - userProfile.point}점 부족합니다.")
            
            transaction = RewardTransaction.objects.create(
                user=user,
                reward=reward,
                expire_at=timezone.now() + timedelta(days=reward.valid_days),
            )
            userProfile.point -= reward.point
            userProfile.save()
            return success_response(RewardTransactionSerializer(transaction).data, "리워드 교환 완료")
        except Exception as e:
            return error_response(str(e), "INTERNAL_SERVER_ERROR")