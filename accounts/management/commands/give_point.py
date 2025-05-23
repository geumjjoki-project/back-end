from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

class Command(BaseCommand):
    help = "전체 유저 또는 특정 유저에게 포인트를 지급합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="포인트를 지급할 유저의 username (생략 시 전체 유저)"
        )
        parser.add_argument(
            "--point",
            type=int,
            default=10000,
            help="지급할 포인트 (기본값: 10000)"
        )

    def handle(self, *args, **options):
        username = options.get("username")
        point = options.get("point")

        if username:
            try:
                user = get_user_model().objects.get(username=username)
                profile = user.user_profile
                profile.point += point
                profile.save(update_fields=["point"])
                self.stdout.write(self.style.SUCCESS(f"{username}에게 {point}포인트 지급 완료"))
            except get_user_model().DoesNotExist:
                self.stderr.write(f"해당 username을 가진 유저가 존재하지 않습니다: {username}")
            except UserProfile.DoesNotExist:
                self.stderr.write(f"해당 유저에 대한 프로필이 존재하지 않습니다: {username}")
        else:
            profiles = UserProfile.objects.select_related("user").all()
            for profile in profiles:
                profile.point += point
            UserProfile.objects.bulk_update(profiles, ["point"], batch_size=1000)
            self.stdout.write(self.style.SUCCESS(f"전체 유저에게 {point}포인트 지급 완료"))