from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Challenge, UserChallenge
from .serializers import (
    ChallengeListSerializer,
    ChallengeDetailSerializer,
    UserChallengeListSerializer,
    UserChallengeDetailSerializer
)
from django.utils import timezone
from .pagination import CustomChallengePagination
from .utils.response import success_response, error_response
from datetime import datetime, timedelta
from django.db.models import Q, Sum
from expenses.models import Expense
from decimal import Decimal, InvalidOperation

# 정렬 허용 필드
ALLOWED_SORT_FIELDS = [
    'start_date',
    'end_date',
    'goal_amount',
    'point',
    'computed_status'
]

# 유저 챌린지 상태 업데이트 헬퍼
def judge_user_challenge_status(user_challenge):
    today = timezone.now().date()

    if user_challenge.status == '도전중' and today > user_challenge.end_date.date():
        user_profile = user_challenge.user.user_profile
        challenge = user_challenge.challenge

        if user_challenge.total_expense <= user_challenge.target_expense:
            user_challenge.status = '성공'

            # 경험치 및 포인트 계산
            gained_exp = challenge.point * 10
            gained_point = challenge.point

            user_profile.exp += gained_exp
            user_profile.point += gained_point

            # 레벨 계산
            if user_profile.exp >= 300000:
                user_profile.level = 5
            elif user_profile.exp >= 100000:
                user_profile.level = 4
            elif user_profile.exp >= 30000:
                user_profile.level = 3
            elif user_profile.exp >= 10000:
                user_profile.level = 2
            else:
                user_profile.level = 1

            user_profile.save(update_fields=['exp', 'point', 'level'])

        else:
            user_challenge.status = '실패'

        user_challenge.save(update_fields=['status'])


class ChallengeBaseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pass


class ChallengeView(ChallengeBaseView):
    def get(self, request):
        try:
            # 쿼리 파라미터
            title = request.GET.get('title')
            content = request.GET.get('content')
            goal_amount = request.GET.get('goal_amount')
            goal_days = request.GET.get('goal_days')
            category = request.GET.get('category')
            point = request.GET.get('point')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            is_active = request.GET.get('is_active')
            status_param = request.GET.get('status')
            
            qs = Challenge.objects.all()
            
            # 필터링
            if title:
                qs = qs.filter(title__icontains=title)
            if content:
                qs = qs.filter(content__icontains=content)
            if goal_amount:
                try:
                    goal_amount = Decimal(goal_amount)
                except InvalidOperation:
                    return error_response("goal_amount 형식 오류", code=400)
                qs = qs.filter(goal_amount=goal_amount)
            if goal_days:
                try:
                    goal_days = int(goal_days)
                except ValueError:
                    return error_response("goal_days 형식 오류", code=400)
                qs = qs.filter(goal_days=goal_days)
            if category:
                try:
                    category = int(category)
                except ValueError:
                    return error_response("category 형식 오류", code=400)
                qs = qs.filter(category_id=category)
            if point:
                try:
                    point = int(point)
                except ValueError:
                    return error_response("point 형식 오류", code=400)
                qs = qs.filter(point=point)
            if start_date:
                try:
                    start_date = datetime.fromisoformat(start_date).date()
                except ValueError:
                    return error_response("start_date 형식 오류", code=400)
                qs = qs.filter(start_date__gte=start_date)
            if end_date:
                try:
                    end_date = datetime.fromisoformat(end_date).date()
                except ValueError:
                    return error_response("end_date 형식 오류", code=400)
                qs = qs.filter(end_date__lte=end_date)
            if is_active:
                if is_active.lower() in ['true', '1', 'yes']:
                    qs = qs.filter(is_active=True)
                elif is_active.lower() in ['false', '0', 'no']:
                    qs = qs.filter(is_active=False)
                else:
                    return error_response("is_active는 true 또는 false여야 합니다.", "INVALID_IS_ACTIVE_PARAM")

            
            sort = request.GET.get('sort', '-start_date')
            sort_field = sort.lstrip('-')
            reverse = sort.startswith('-')
            
            if sort_field != 'computed_status':
                qs = qs.order_by(sort)

            serializer_all = ChallengeListSerializer(qs, many=True)
            full_list = serializer_all.data
            if status_param := request.GET.get('status'):
                full_list = [
                    c for c in full_list
                    if c['computed_status'] == status_param
                ]
                
            rank = {"도전가능":0, "도전불가":1, "예정":2, "종료":3}
            
            def sort_key(item):
                # 1) status key
                status_key = rank.get(item['computed_status'], 99)

                # 2) 두 번째 키: item[sort_field] 를 적절히 타입 변환
                raw = item.get(sort_field)
                if sort_field == 'goal_amount':
                    val = Decimal(raw)
                elif sort_field in ('goal_days', 'point'):
                    val = int(raw)
                elif sort_field in ('start_date', 'end_date'):
                    # datetime 섹션: timestamp 로 비교
                    val = datetime.fromisoformat(raw).timestamp()
                else:
                    # 문자열 필드라면 그대로
                    val = raw

                # 3) 내림차순(reverse)일 땐 숫자는 부호 반전
                if reverse and isinstance(val, (int, float, Decimal)):
                    val = -val

                return (status_key, val)
                
            full_list = sorted(full_list, key=sort_key)

            paginator = CustomChallengePagination()
            page_list = paginator.paginate_queryset(full_list, request)
            paginated = paginator.get_paginated_response(page_list).data

            return success_response(paginated)

        except Exception as e:
            return error_response(str(e), error_code="SERVER_ERROR", code=500)



class ChallengeDetailView(ChallengeBaseView):
    """단일 챌린지 상세조회"""
    def get(self, request, challenge_id):
        try:
            challenge = Challenge.objects.get(pk=challenge_id)
            serializer = ChallengeDetailSerializer(challenge)
            return success_response(serializer.data)
        except Challenge.DoesNotExist:
            return error_response(
                "해당 챌린지를 찾을 수 없습니다.",
                error_code="CHALLENGE_NOT_FOUND",
                code=404
            )
        except Exception as e:
            return error_response(str(e), error_code="SERVER_ERROR", code=500)


class UserChallengeView(ChallengeBaseView):
    """내 챌린지 목록 (도전중/성공/실패)"""
    def get(self, request):
        user = request.user
        type_param = request.GET.get('type')
        type_map = {"1": "도전중", "2": "성공", "3": "실패"}
        qs = UserChallenge.objects.filter(user=user)
        if type_param in type_map:
            qs = qs.filter(status=type_map[type_param])

        # 상태 자동 갱신
        for uc in qs:
            if uc.status == '도전중':
                judge_user_challenge_status(uc)

        paginator = CustomChallengePagination()
        page_qs = paginator.paginate_queryset(qs, request)
        serializer = UserChallengeListSerializer(page_qs, many=True)
        data = paginator.get_paginated_response(serializer.data).data
        return success_response(data)


class UserChallengeDetailView(ChallengeBaseView):
    """내 챌린지 상세조회"""
    def get(self, request, user_challenge_id):
        user = request.user
        try:
            uc = UserChallenge.objects.get(pk=user_challenge_id, user=user)
            if uc.status == '도전중':
                judge_user_challenge_status(uc)
            serializer = UserChallengeDetailSerializer(uc)
            return success_response(serializer.data)
        except UserChallenge.DoesNotExist:
            return error_response(
                "해당 유저챌린지를 찾을 수 없습니다.",
                error_code="USER_CHALLENGE_NOT_FOUND",
                code=404
            )
        except Exception as e:
            return error_response(str(e), error_code="SERVER_ERROR", code=500)


class ChallengeJoinView(ChallengeBaseView):
    """챌린지 참여"""
    def post(self, request, challenge_id):
        user = request.user
        try:
            challenge = Challenge.objects.get(pk=challenge_id)
            now = timezone.now()

            # 1. 종료된 챌린지인지
            if challenge.computed_status == "종료" or challenge.end_date < now:
                return error_response(
                    "종료된 챌린지에는 도전할 수 없습니다.",
                    error_code="CHALLENGE_ALREADY_FINISHED",
                    code=400
                )

            # 2. 기간 체크
            period = (challenge.end_date.date() - challenge.start_date.date()).days + 1
            if period < challenge.goal_days:
                return error_response(
                    "챌린지 기간이 목표 기간보다 짧아 도전할 수 없습니다.",
                    error_code="PERIOD_TOO_SHORT",
                    code=400
                )

            # 3. 최근 소비 검증 (7/28일 챌린지)
            previous_expense = 0
            target_expense = challenge.goal_amount
            if challenge.goal_days in (7, 28):
                end_date = (now - timedelta(days=1)).date()
                start_date = (now - timedelta(days=challenge.goal_days)).date()

                if not challenge.category:
                    return error_response(
                        "카테고리가 지정되지 않은 챌린지는 입장 제한 검증을 할 수 없습니다.",
                        error_code="CATEGORY_REQUIRED",
                        code=400
                    )
                root = challenge.category.get_root_category()
                qs_exp = Expense.objects.filter(
                    user=user,
                    date__gte=start_date,
                    date__lte=end_date
                ).filter(
                    Q(category=root) | Q(category__parent_category=root)
                )
                previous_expense = qs_exp.aggregate(total=Sum("amount"))['total'] or 0
                if previous_expense < challenge.goal_amount:
                    return error_response(
                        f"지난 {challenge.goal_days}일간({start_date}~{end_date}) {root.name}에서 "
                        f"{challenge.goal_amount}원 이상 소비해야 합니다. 현재: {int(previous_expense)}원",
                        error_code="NOT_ENOUGH_EXPENSE",
                        code=400
                    )
                target_expense = max(0, previous_expense - challenge.goal_amount)

            # 4. 중복참여 방지
            if UserChallenge.objects.filter(
                user=user, challenge=challenge, status="도전중"
            ).exists():
                return error_response(
                    "이미 도전중인 챌린지입니다.",
                    error_code="ALREADY_IN_PROGRESS",
                    code=400
                )

            # 5. 같은 카테고리 중복 참여 방지
            if challenge.category and UserChallenge.objects.filter(
                user=user, challenge__category=challenge.category, status="도전중"
            ).exclude(challenge=challenge).exists():
                return error_response(
                    "이미 같은 카테고리의 도전중 챌린지가 있습니다.",
                    error_code="ALREADY_IN_PROGRESS_CATEGORY",
                    code=400
                )

            # 6. 도전가능 상태만
            if challenge.computed_status != "도전가능":
                return error_response(
                    "아직 도전이 불가능한 챌린지입니다.",
                    error_code="NOT_JOINABLE",
                    code=400
                )

            # 7. 생성
            uc = UserChallenge.create_for_user(
                user=user,
                challenge=challenge,
                status="도전중",
                previous_expense=previous_expense,
                target_expense=target_expense,
                total_expense=0
            )
            return success_response({"user_challenge_id": uc.user_challenge_id})

        except Challenge.DoesNotExist:
            return error_response(
                "해당 챌린지를 찾을 수 없습니다.",
                error_code="CHALLENGE_NOT_FOUND",
                code=404
            )
        except Exception as e:
            return error_response(str(e), error_code="SERVER_ERROR", code=500)
