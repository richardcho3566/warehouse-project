# set_staff_user.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "warehouse_project.settings")
django.setup()

from django.contrib.auth.models import User

user = User.objects.get(username='wbcho')
user.is_staff = True
user.is_superuser = True  # 혹시라도 빠졌으면 같이 설정
user.save()

print("✅ 'wbcho' 계정에 관리자 권한 부여 완료!")
