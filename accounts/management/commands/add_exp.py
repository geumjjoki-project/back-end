from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

def calculate_level(exp: int) -> int:
    if exp >= 100000:
        return 5
    elif exp >= 50000:
        return 4
    elif exp >= 30000:
        return 3
    elif exp >= 10000:
        return 2
    return 1

class Command(BaseCommand):
    help = "특정 유저에게 경험치를 지급하고 레벨을 갱신합니다."

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, required=True, help="유저명")
        parser.add_argument("--exp", type=int, required=True, help="추가할 경험치 양")

    def handle(self, *args, **options):
        username = options["username"]
        add_exp = options["exp"]

        try:
            user = User.objects.get(username=username)
            profile = user.user_profile

            profile.exp += add_exp
            profile.level = calculate_level(profile.exp)
            profile.save(update_fields=["exp", "level"])

            self.stdout.write(
                self.style.SUCCESS(
                    f"{username} 님에게 {add_exp} 경험치를 지급했습니다. 현재 EXP: {profile.exp}, 레벨: {profile.level}"
                )
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("해당 username을 가진 사용자가 존재하지 않습니다."))
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR("해당 유저에 연결된 프로필이 존재하지 않습니다."))
