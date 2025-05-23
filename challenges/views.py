from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Challenge, UserChallenge
from .serializers import ChallengeListSerializer, ChallengeDetailSerializer, UserChallengeListSerializer, UserChallengeDetailSerializer
from django.utils import timezone
from .pagniation import CustomChallengePagination
from .utils.response import success_response, error_response
from datetime import timedelta
from django.db.models import Q, Sum
from expenses.models import Expense

def judge_user_challenge_status(user_challenge):
    now = timezone.now().date()
    if user_challenge.status == '도전중' and now > user_challenge.end_date.date():
        if user_challenge.total_expense <= user_challenge.target_expense:
            user_challenge.status = '성공'
        else:
            user_challenge.status = '실패'
        user_challenge.save(update_fields=['status'])

class ChallengeBaseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pass

# 전체 조회
class ChallengeView(ChallengeBaseView):
    def get(self, request):
        try:
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            sort = request.GET.get('sort', 'date')
            size = request.GET.get('size')

            challenges = Challenge.objects.all()
            if start_date:
                challenges = challenges.filter(start_date__gte=start_date)
            if end_date:
                challenges = challenges.filter(end_date__lte=end_date)
            if sort == 'date':
                challenges = challenges.order_by('-start_date')
            else:
                return error_response("지원되지 않는 정렬 기준입니다.", error_code="UNSUPPORTED_SORT", code=400)

            paginator = CustomChallengePagination()
            if size:
                paginator.page_size = int(size)
            paginated_qs = paginator.paginate_queryset(challenges, request)
            serializer = ChallengeListSerializer(paginated_qs, many=True)
            paginated_data = paginator.get_paginated_response(serializer.data).data
            return success_response(paginated_data)
        except Exception as e:
            return error_response(str(e), error_code="SERVER_ERROR", code=500)

# 상세 조회
class ChallengeDetailView(ChallengeBaseView):
    def get(self, request, challenge_id):
        try:
            challenge = Challenge.objects.get(pk=challenge_id)
            serializer = ChallengeDetailSerializer(challenge)
            return success_response(serializer.data)
        except Challenge.DoesNotExist:
            return error_response("해당 챌린지를 찾을 수 없습니다.", error_code="CHALLENGE_NOT_FOUND", code=404)
        except Exception as e:
            return error_response(str(e), error_code="SERVER_ERROR", code=500)


# 내 챌린지 리스트 보기 (도전중, 성공, 실패)
class UserChallengeView(ChallengeBaseView):
    def get(self, request):
        user = request.user
        type_param = request.GET.get('type')
        type_map = {
            "1": "도전중",
            "2": "성공",
            "3": "실패"
        }
        queryset = UserChallenge.objects.filter(user=user)
        if type_param in type_map:
            queryset = queryset.filter(status=type_map[type_param])

        for uc in queryset:
            if uc.status == '도전중':
                judge_user_challenge_status(uc)
                
        paginator = CustomChallengePagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = UserChallengeListSerializer(paginated_qs, many=True)
        paginated_data = paginator.get_paginated_response(serializer.data).data
        return success_response(paginated_data)

# 내 챌린지 상세조회
class UserChallengeDetailView(ChallengeBaseView):
    def get(self, request, user_challenge_id):
        user = request.user
        try:
            user_challenge = UserChallenge.objects.get(pk=user_challenge_id, user=user)
            if user_challenge.status == '도전중':
                judge_user_challenge_status(user_challenge)
            serializer = UserChallengeDetailSerializer(user_challenge)
            return success_response(serializer.data)
        except UserChallenge.DoesNotExist:
            return error_response("해당 유저챌린지를 찾을 수 없습니다.", error_code="USER_CHALLENGE_NOT_FOUND", code=404)
        except Exception as e:
            return error_response(str(e), error_code="SERVER_ERROR", code=500)

# 챌린지 참여
class ChallengeJoinView(ChallengeBaseView):
    def post(self, request, challenge_id):
        user = request.user
        try:
            challenge = Challenge.objects.get(pk=challenge_id)
            now = timezone.now()

            # 1. 종료 챌린지/종료일 체크
            if challenge.computed_status == "종료" or challenge.end_date < now:
                return error_response("종료된 챌린지에는 도전할 수 없습니다.", error_code="CHALLENGE_ALREADY_FINISHED", code=400)

            # 2. 챌린지 기간 체크
            period_days = (challenge.end_date.date() - challenge.start_date.date()).days + 1
            if period_days < challenge.goal_days:
                return error_response("챌린지 기간이 목표 기간보다 짧아 도전할 수 없습니다.", error_code="PERIOD_TOO_SHORT", code=400)

            # 3. 최근 기간 소비내역 체크 (7/28일 챌린지 한정)
            previous_expense = 0
            target_expense = challenge.goal_amount
            if challenge.goal_days in (7, 28):
                period_days = challenge.goal_days
                period_end = (now - timedelta(days=1)).date() # 오늘 제외
                period_start = (now - timedelta(days=period_days)).date()
                category = challenge.category
                if not category:
                    return error_response("카테고리가 지정되지 않은 챌린지는 입장 제한 검증을 할 수 없습니다.",
                                         error_code="CATEGORY_REQUIRED", code=400)
                root_category = category.get_root_category() if hasattr(category, "get_root_category") else category

                # 하위 카테고리까지 포함해서 집계
                expenses_qs = Expense.objects.filter(
                    user=user,
                    date__gte=period_start,
                    date__lte=period_end,
                ).filter(
                    Q(category=root_category) | Q(category__parent_category=root_category)
                )
                previous_expense = expenses_qs.aggregate(total=Sum("amount"))["total"] or 0

                # 참가 조건: 지난 기간 소비가 목표금액 이상이어야 함
                if previous_expense < challenge.goal_amount:
                    category_name = root_category.name if root_category else "해당 카테고리"
                    return error_response(
                        f"지난 {challenge.goal_days}일간({period_start} ~ {period_end}) '{category_name}' 카테고리에서 "
                        f"{challenge.goal_amount}원 이상 소비해야 참가할 수 있습니다. "
                        f"현재 사용금액: {int(previous_expense)}원",
                        error_code="NOT_ENOUGH_EXPENSE",
                        code=400
                    )
                # 목표지출 = 이전 소비 - 절약 목표(정책에 따라 조정 가능)
                target_expense = max(0, previous_expense - challenge.goal_amount)

            # 4. 동일 챌린지 '도전중' 중복참여 막기
            if UserChallenge.objects.filter(
                user=user,
                challenge=challenge,
                status="도전중"
            ).exists():
                return error_response("이미 도전중인 챌린지입니다.", error_code="ALREADY_IN_PROGRESS", code=400)

            # 5. 동일 카테고리 '도전중' 챌린지 중복참여 막기 (다른 챌린지에서)
            if challenge.category:
                same_category_in_progress = UserChallenge.objects.filter(
                    user=user,
                    challenge__category=challenge.category,
                    status="도전중"
                ).exclude(challenge=challenge).exists()
                if same_category_in_progress:
                    return error_response("이미 같은 카테고리의 도전중 챌린지에 참여하고 있습니다.",
                                         error_code="ALREADY_IN_PROGRESS_CATEGORY", code=400)

            # 6. '도전가능' 상태만 참여 허용
            if challenge.computed_status != "도전가능":
                return error_response("아직 도전이 불가능한 챌린지입니다.", error_code="NOT_JOINABLE", code=400)

            # 7. UserChallenge 생성
            user_challenge = UserChallenge.create_for_user(
                user=user,
                challenge=challenge,
                status="도전중",
                previous_expense=previous_expense,
                target_expense=target_expense,
                total_expense=0,  # 생성 시점엔 0
            )

            return success_response({"user_challenge_id": user_challenge.user_challenge_id})

        except Challenge.DoesNotExist:
            return error_response("해당 챌린지를 찾을 수 없습니다.", error_code="CHALLENGE_NOT_FOUND", code=404)
        except Exception as e:
            return error_response(str(e), error_code="SERVER_ERROR", code=500)