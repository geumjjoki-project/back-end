from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from .models import UserProfile
import logging

logger = logging.getLogger('accounts')
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Populates user information from social network signup.
        """
        user = super().populate_user(request, sociallogin, data)

        # 추가 정보 가져오기 (카카오 예시)
        if sociallogin.account.provider == 'kakao':
            try:
                kakao_account = sociallogin.account.extra_data.get('kakao_account')
                profile = kakao_account.get('profile')
                nickname = profile.get('nickname')
                profile_image = profile.get('profile_image_url')
                email = kakao_account.get('email')
                logger.debug(f"kakao_account: {kakao_account}")
                
                if nickname:
                    user.nickname = nickname  # user_nickname -> nickname으로 수정
                
                if profile_image:
                    user.profile_image = profile_image
                
                if email:
                    user.email = email
                
                
            except (KeyError, AttributeError):
                pass

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Saves the user and creates UserProfile
        """
        # 먼저 User 객체를 저장
        user = super().save_user(request, sociallogin, form)
        
        # User 객체가 저장된 후에 UserProfile 생성
        try:
            # 디버깅을 위한 로그 추가
            print(f"Attempting to create UserProfile for user: {user.email}")
            
            # UserProfile이 이미 존재하는지 확인
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'level': 1,
                    'exp': 0,
                    'mileage': 0,
                    'average_income': 0.00
                }
            )
            
            if created:
                print(f"Successfully created UserProfile for user: {user.email}")
            else:
                print(f"UserProfile already exists for user: {user.email}")
                
        except Exception as e:
            print(f"Error creating UserProfile: {str(e)}")
            # 에러의 구체적인 정보 출력
            import traceback
            print(traceback.format_exc())
            raise  # 에러를 상위로 전파하여 디버깅을 용이하게 함
        
        return user


class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        user = super().save_user(request, user, form, commit=False)

        # 일반 회원가입 시에도 user_nickname 등 추가 필드 처리 가능
        # data = form.cleaned_data
        # user.user_nickname = data.get('user_nickname')

        if commit:
            user.save()
        return user

    # --- 아래는 소셜 로그인 사용자의 비밀번호 관련 처리 (선택 사항) ---

    # def render_change_password_form(self, request, form):
    #     # 소셜 로그인 사용자의 비밀번호 변경 폼 비활성화
    #     if not request.user.has_usable_password():
    #          # 또는 메시지와 함께 리디렉션 등
    #         return None # 템플릿에서 None을 확인하여 폼 숨김
    #     return super().render_change_password_form(request, form)

    # def render_set_password_form(self, request, form):
    #     # 소셜 로그인 사용자의 초기 비밀번호 설정 폼 비활성화
    #     if not request.user.has_usable_password() and request.user.socialaccount_set.exists():
    #         return None
    #     return super().render_set_password_form(request, form)

    # def has_usable_password(self, user):
    #     # 소셜 로그인 사용자는 비밀번호가 없어도 로그인이 가능하도록 처리
    #     # 또는 비밀번호 없이 가입 후 별도 설정 유도
    #     if user.socialaccount_set.exists():
    #         return True # True를 반환하여 비밀번호 확인 절차 우회 가능
    #     return super().has_usable_password(user)
