from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.db.models import Q
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiResponse,
    OpenApiExample,
    inline_serializer,
)

from .models import Reward, RewardTransaction
from .serializers import (
    RewardListSerializer,
    RewardTransactionSerializer,
    RewardSerializer,
)
from .pagination import CustomPageNumberPagination

# ------------------------------------------
# Swagger 쿼리 파라미터 정의
# ------------------------------------------
reward_list_parameters = [
    OpenApiParameter(
        name="is_active",
        type=OpenApiTypes.BOOL,
        description="활성화 여부 (true/false)",
        required=False,
    ),
    OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        description="검색어 (이름, 설명)",
        required=False,
    ),
    OpenApiParameter(
        name="min_point",
        type=OpenApiTypes.INT,
        description="최소 비용",
        required=False,
    ),
    OpenApiParameter(
        name="max_point",
        type=OpenApiTypes.INT,
        description="최대 비용",
        required=False,
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description="정렬 기준 (point, is_active)",
        required=False,
    ),
]

reward_transaction_list_parameters = [
    OpenApiParameter(
        name="status",
        type=OpenApiTypes.INT,
        description="교환 상태 (0: 사용 가능, 1: 사용 완료, 2: 만료, 3: 중지)",
        required=False,
    ),
    OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        description="리워드 이름 또는 설명 검색",
        required=False,
    ),
    OpenApiParameter(
        name="start_date",
        type=OpenApiTypes.DATE,
        description="시작일 (YYYY-MM-DD)",
        required=False,
    ),
    OpenApiParameter(
        name="end_date",
        type=OpenApiTypes.DATE,
        description="종료일 (YYYY-MM-DD)",
        required=False,
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description="정렬 기준: redeemed_at, expire_at",
        required=False,
    ),
]

# 공통 에러 응답 스키마
error_response_schema = inline_serializer(
    name="ErrorResponse",
    fields={
        "status": serializers.CharField(),
        "message": serializers.CharField(),
        "error_code": serializers.CharField(),
    },
)


# ------------------------------------------
# 리워드 목록
# ------------------------------------------
@extend_schema(
    summary="전체 리워드 목록 조회",
    parameters=reward_list_parameters,
    responses={
        200: RewardListSerializer(many=True),
        400: OpenApiResponse(
            response=error_response_schema,
            description="잘못된 요청",
            examples=[
                OpenApiExample(
                    name="Invalid point",
                    summary="min_point가 숫자가 아님",
                    value={
                        "status": "error",
                        "message": "min_point 및 max_point는 정수여야 합니다.",
                        "error_code": "INVALID_point_PARAM",
                    },
                ),
                OpenApiExample(
                    name="Invalid is_active",
                    summary="is_active가 true/false가 아님",
                    value={
                        "status": "error",
                        "message": "is_active는 true 또는 false여야 합니다.",
                        "error_code": "INVALID_IS_ACTIVE_PARAM",
                    },
                ),
            ],
        ),
        500: OpenApiResponse(
            response=error_response_schema,
            description="서버 내부 오류",
            examples=[
                OpenApiExample(
                    name="Internal Error",
                    summary="처리되지 않은 예외 발생",
                    value={
                        "status": "error",
                        "message": "예상치 못한 오류가 발생했습니다.",
                        "error_code": "INTERNAL_SERVER_ERROR",
                    },
                ),
            ],
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reward_list(request):
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
            return Response(
                {
                    "status": "error",
                    "message": "is_active는 true 또는 false여야 합니다.",
                    "error_code": "INVALID_IS_ACTIVE_PARAM",
                },
                status=400,
            )

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
        return Response(
            {
                "status": "error",
                "message": "min_point 및 max_point는 정수여야 합니다.",
                "error_code": "INVALID_point_PARAM",
            },
            status=400,
        )

    if ordering:
        fields = [f.strip() for f in ordering.split(",") if f.strip()]
        try:
            rewards = rewards.order_by(*fields)
        except:
            rewards = rewards.order_by(*DEFAULT_ORDERING)
    else:
        rewards = rewards.order_by(*DEFAULT_ORDERING)

    paginator = CustomPageNumberPagination()
    paginated = paginator.paginate_queryset(rewards, request)
    serializer = RewardListSerializer(paginated, many=True)
    return paginator.get_paginated_response(
        {"status": "success", "data": serializer.data}
    )


# ------------------------------------------
# 리워드 상세조회
# ------------------------------------------
@extend_schema(
    summary="리워드 상세 조회",
    # path parameter 정의
    parameters=[
        OpenApiParameter(
            name="reward_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="조회할 리워드의 ID",
            required=True,
        ),
    ],
    responses={
        200: RewardSerializer,
        500: OpenApiResponse(
            response=error_response_schema,
            description="서버 내부 오류",
            examples=[
                OpenApiExample(
                    name="Internal Error",
                    summary="처리되지 않은 예외 발생",
                    value={
                        "status": "error",
                        "message": "예상치 못한 오류가 발생했습니다.",
                        "error_code": "INTERNAL_SERVER_ERROR",
                    },
                ),
            ],
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reward_detail(request, reward_id):
    reward = get_object_or_404(Reward, reward_id=reward_id)
    serializer = RewardSerializer(reward)
    return Response({"status": "success", "data": serializer.data})


# ------------------------------------------
# 리워드 교환 목록
# ------------------------------------------
@extend_schema(
    summary="리워드 교환 목록 조회",
    parameters=reward_transaction_list_parameters,
    responses={
        200: RewardTransactionSerializer(many=True),
        400: OpenApiResponse(
            response=error_response_schema,
            description="파라미터 오류",
            examples=[
                OpenApiExample(
                    name="Invalid status",
                    summary="status가 정수가 아님",
                    value={
                        "status": "error",
                        "message": "status는 정수여야 합니다.",
                        "error_code": "INVALID_STATUS_PARAM",
                    },
                ),
                OpenApiExample(
                    name="Invalid start_date",
                    summary="날짜 형식 오류",
                    value={
                        "status": "error",
                        "message": "start_date는 YYYY-MM-DD 형식이어야 합니다.",
                        "error_code": "INVALID_START_DATE",
                    },
                ),
                OpenApiExample(
                    name="Invalid ordering",
                    summary="허용되지 않은 정렬 기준",
                    value={
                        "status": "error",
                        "message": "허용되지 않은 정렬 기준입니다.",
                        "error_code": "INVALID_ORDERING_PARAM",
                    },
                ),
            ],
        ),
        500: OpenApiResponse(
            response=error_response_schema,
            description="서버 내부 오류",
            examples=[
                OpenApiExample(
                    name="Internal Error",
                    summary="처리되지 않은 예외 발생",
                    value={
                        "status": "error",
                        "message": "예상치 못한 오류가 발생했습니다.",
                        "error_code": "INTERNAL_SERVER_ERROR",
                    },
                ),
            ],
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reward_transaction_list(request):
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
            return Response(
                {
                    "status": "error",
                    "message": "status는 정수여야 합니다.",
                    "error_code": "INVALID_STATUS_PARAM",
                },
                status=400,
            )

    if start_date:
        parsed_start = parse_date(start_date)
        if not parsed_start:
            return Response(
                {
                    "status": "error",
                    "message": "start_date는 YYYY-MM-DD 형식이어야 합니다.",
                    "error_code": "INVALID_START_DATE",
                },
                status=400,
            )
        transactions = transactions.filter(redeemed_at__date__gte=parsed_start)

    if end_date:
        parsed_end = parse_date(end_date)
        if not parsed_end:
            return Response(
                {
                    "status": "error",
                    "message": "end_date는 YYYY-MM-DD 형식이어야 합니다.",
                    "error_code": "INVALID_END_DATE",
                },
                status=400,
            )
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
        return Response(
            {
                "status": "error",
                "message": "허용되지 않은 정렬 기준입니다.",
                "error_code": "INVALID_ORDERING_PARAM",
            },
            status=400,
        )

    transactions = transactions.order_by(ordering)

    paginator = CustomPageNumberPagination()
    paginated = paginator.paginate_queryset(transactions, request)
    serializer = RewardTransactionSerializer(paginated, many=True)
    return paginator.get_paginated_response(
        {"status": "success", "data": serializer.data}
    )


# ------------------------------------------
# 교환 상세조회 (본인만 가능)
# ------------------------------------------
@extend_schema(
    summary="리워드 교환 상세 조회",
    responses={
        200: RewardTransactionSerializer,
        403: OpenApiResponse(
            response=error_response_schema,
            description="권한 없음",
            examples=[
                OpenApiExample(
                    name="Not Owner",
                    summary="접근한 사용자가 교환 주인이 아님",
                    value={
                        "status": "error",
                        "message": "본인의 교환내역만 조회할 수 있습니다.",
                        "error_code": "REWARD_TRANSACTION_PERMISSION_DENIED",
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            response=error_response_schema,
            description="존재하지 않는 교환 ID",
            examples=[
                OpenApiExample(
                    name="Not Found",
                    summary="존재하지 않는 교환 ID",
                    value={
                        "status": "error",
                        "message": "해당 리워드 교환 기록이 존재하지 않습니다.",
                        "error_code": "REWARD_TRANSACTION_NOT_FOUND",
                    },
                )
            ],
        ),
        500: OpenApiResponse(
            response=error_response_schema,
            description="서버 내부 오류",
            examples=[
                OpenApiExample(
                    name="Internal Error",
                    summary="처리되지 않은 예외 발생",
                    value={
                        "status": "error",
                        "message": "예상치 못한 오류가 발생했습니다.",
                        "error_code": "INTERNAL_SERVER_ERROR",
                    },
                ),
            ],
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reward_transaction_detail(request, reward_transaction_id):
    transaction = RewardTransaction.objects.select_related("reward").get(
        pk=reward_transaction_id
    )

    if transaction.user != request.user:
        return Response(
            {
                "status": "error",
                "message": "본인의 교환내역만 조회할 수 있습니다.",
                "error_code": "REWARD_TRANSACTION_PERMISSION_DENIED",
            },
            status=403,
        )

    serializer = RewardTransactionSerializer(transaction)
    return Response({"status": "success", "data": serializer.data})
