from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from inventory.models import Profile


class Command(BaseCommand):
    help = "Create missing Profile rows for existing users."

    def handle(self, *args, **options):
        created_count = 0
        for user in User.objects.all():
            _, created = Profile.objects.get_or_create(user=user, defaults={"grade": "GRADE1"})
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Profile 보정 완료: 생성 {created_count}건"))
