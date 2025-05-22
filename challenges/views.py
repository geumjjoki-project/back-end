from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Challenge, UserChallenge
from .serializers import ChallengeListSerializer, ChallengeDetailSerializer, UserChallengeListSerializer
from datetime import datetime
from rest_framework import status

# 전체 조회
@api_view(['GET'])
def challenge_list(request):
    try:
        # Query Parameters
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 10))
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        sort = request.GET.get('sort', 'date')

        # 챌린지 기본 쿼리셋
        challenges = Challenge.objects.all()

        # 날짜 필터링
        if start_date:
            challenges = challenges.filter(start_date__gte=start_date)
        if end_date:
            challenges = challenges.filter(end_date__lte=end_date)

        # 정렬
        if sort == 'date':
            challenges = challenges.order_by('-start_date')
        else:
            return Response({
                "status": "error",
                "message": "지원되지 않는 정렬 기준입니다.",
                "error_code": "UNSUPPORTED_SORT"
            }, status=400)

        # 페이지네이션
        paginator = Paginator(challenges, size)
        page_obj = paginator.get_page(page)

        # 직렬화
        serializer = ChallengeListSerializer(page_obj, many=True)

        return Response({
            "status": "success",
            "data": serializer.data,
            "total_count": paginator.count
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "error_code": "SERVER_ERROR"
        }, status=500)

# 상세 조회
@api_view(['GET'])
def challenge_detail(request, challenge_id):
    try:
        challenge = Challenge.objects.get(pk=challenge_id)
        serializer = ChallengeDetailSerializer(challenge)
        return Response({
            "status": "success",
            "data": serializer.data
        })
    except Challenge.DoesNotExist:
        return Response({
            "status": "error",
            "message": "해당 챌린지를 찾을 수 없습니다.",
            "error_code": "CHALLENGE_NOT_FOUND"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            "error_code": "SERVER_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 진행 중, 성공, 실패
@api_view(['GET'])
def user_challenge_list_view(request):
    type_param = request.GET.get('type')
    user_param = request.GET.get('user')

    # 필수 파라미터 검증
    if type_param is None:
        return Response({
            "status": "error",
            "message": "type 파라미터는 필수입니다.",
            "error_code": "MISSING_TYPE"
        }, status=400)

    if user_param is None:
        return Response({
            "status": "error",
            "message": "user 파라미터는 필수입니다.",
            "error_code": "MISSING_USER"
        }, status=400)

    # type 매핑
    type_map = {
        0: "진행중",
        1: "성공",
        2: "실패"
    }

    try:
        type_int = int(type_param)
        user_id = int(user_param)
    except ValueError:
        return Response({
            "status": "error",
            "message": "type과 user는 정수여야 합니다.",
            "error_code": "INVALID_PARAM_FORMAT"
        }, status=400)

    if type_int not in type_map:
        return Response({
            "status": "error",
            "message": "지원하지 않는 type 값입니다.",
            "error_code": "INVALID_TYPE"
        }, status=400)

    # 필터링된 쿼리셋
    queryset = UserChallenge.objects.filter(
        user_id=user_id,
        status=type_map[type_int]
    )

    serializer = UserChallengeListSerializer(queryset, many=True)
    return Response({
        "status": "success",
        "data": serializer.data
    })