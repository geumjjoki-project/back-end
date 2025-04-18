from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

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

                if nickname:
                    user.user_nickname = nickname # user_nickname 필드에 저장

                # 다른 필요한 정보도 여기서 처리 가능
                # 예: 프로필 이미지 URL 저장 등

            except (KeyError, AttributeError):
                # 카카오 응답 구조가 예상과 다를 경우 처리
                pass

        # User 모델의 다른 커스텀 필드 기본값 설정 등 추가 로직 구현 가능
        # user.user_role = 1 # 예시: 소셜 로그인은 특정 역할 부여 등

        return user

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before any accounts are linked/created).
        """
        # 이미 가입된 이메일이지만 소셜 계정과는 연결되지 않은 경우 처리 등
        # 예를 들어, 동일 이메일로 일반 가입한 유저가 소셜 로그인을 시도할 때 연결해주는 로직
        pass


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
