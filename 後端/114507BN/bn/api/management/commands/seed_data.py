# 檔案路徑: api/management/commands/seed_data.py (最終版 - 包含所有模型)

import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from faker import Faker
from api.models import (
    PersonnelProfile, Group, GroupMember, ScoringStandard, VehicleDevice,
    Trip, AiVisionLog, VideoRecord, GroupAnnouncement, SystemAnnouncement,
    ActivationCode, InvitationCode
)
from api.services import calculate_trip_score

fake = Faker('zh_TW')

class Command(BaseCommand):
    help = 'Seeds the database with a complete and large-scale corporate dataset.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Starting FINAL database seeding process..."))

        # --- 1. 清理舊資料 ---
        self.stdout.write("🧹 Cleaning up old data...")
        Trip.objects.all().delete()
        GroupMember.objects.exclude(user__is_superuser=True).delete()
        Group.objects.all().delete()
        PersonnelProfile.objects.exclude(user__is_superuser=True).delete()
        User.objects.filter(is_superuser=False).delete()
        ScoringStandard.objects.all().delete()
        VehicleDevice.objects.all().delete()
        GroupAnnouncement.objects.all().delete()
        SystemAnnouncement.objects.all().delete()
        ActivationCode.objects.all().delete()
        InvitationCode.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✅ Old data cleaned up."))

        # --- 2. 建立啟用碼 ---
        self.stdout.write("🔑 Creating activation codes...")
        ActivationCode.objects.create(notes="北大物流 2025年度啟用碼", max_uses=50)
        ActivationCode.objects.create(notes="合作夥伴 A 公司專用碼", max_uses=10)
        self.stdout.write(self.style.SUCCESS("✅ Activation codes created."))

        # --- 3. 建立評分標準 ---
        self.stdout.write("📝 Creating new scoring standards...")
        events_data = [
            {'event_number': 'A01', 'description': '重度疲勞(閉眼5秒以上)', 'deduction_points': 40},
            {'event_number': 'A02', 'description': '中度疲勞(閉眼3-5秒)', 'deduction_points': 30},
            {'event_number': 'A03', 'description': '使用手機', 'deduction_points': 15},
            {'event_number': 'A04', 'description': '臉部離開', 'deduction_points': 40},
            {'event_number': 'B01', 'description': '切換車道未打方向燈', 'deduction_points': 15},
            {'event_number': 'B02', 'description': '轉彎未打方向燈', 'deduction_points': 15},
            {'event_number': 'B03', 'description': '未保持適當車距', 'deduction_points': 15},
        ]
        scoring_standards = [ScoringStandard.objects.create(**data) for data in events_data]
        self.stdout.write(self.style.SUCCESS(f"✅ {len(scoring_standards)} scoring standards created."))
        
        # --- 4. 建立使用者、Profile 和車機 ---
        # (邏輯與前版相同)
        self.stdout.write("👤 Creating a large number of users and devices...")
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser: raise User.DoesNotExist
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ No superuser found. Please run 'python manage.py createsuperuser' first."))
            return
        admin_user, _ = User.objects.get_or_create(username='joywu', defaults={'first_name': '佳憲', 'last_name': '吳', 'email': 'joywu@example.com'})
        admin_user.set_password('admin1234')
        admin_user.save()
        PersonnelProfile.objects.get_or_create(user=admin_user, defaults={'personnel_number': 'T1056017'})
        created_drivers = []
        for i in range(1, 21):
            user, _ = User.objects.get_or_create(username=f'driver{i:02d}', defaults={'first_name': fake.first_name(), 'last_name': fake.last_name(), 'email': f'driver{i:02d}@example.com'})
            user.set_password('driver1234')
            user.save()
            PersonnelProfile.objects.get_or_create(user=user, defaults={'personnel_number': f'D{1000+i}'})
            created_drivers.append(user)
        devices = [VehicleDevice.objects.get_or_create(device_number=f'MDG-TRUCK-{i:02d}', defaults={'vehicle_type': '貨車', 'activation_date': timezone.now().date()})[0] for i in range(1, 6)]
        self.stdout.write(self.style.SUCCESS(f"✅ Users and devices created."))

        # --- 5. 建立群組並分配成員 ---
        # (邏輯與前版相同)
        self.stdout.write("🏢 Creating 3 groups and assigning members...")
        group_names = ['北區-A組 (長途)', '中區-B組 (市區)', '南區-C組 (急件)']
        groups = [Group.objects.get_or_create(name=name, defaults={'group_number': f'TEAM-{chr(65+i)}', 'created_by': superuser})[0] for i, name in enumerate(group_names)]
        for group in groups:
             GroupMember.objects.get_or_create(group=group, user=superuser, defaults={'role': 'ADMIN'})
             GroupMember.objects.get_or_create(group=group, user=admin_user, defaults={'role': 'ADMIN'})
        for i, user in enumerate(created_drivers):
            GroupMember.objects.get_or_create(group=groups[i % len(groups)], user=user, defaults={'role': 'MEMBER'})
        self.stdout.write(self.style.SUCCESS("✅ Groups created and members assigned."))

        # --- 6. 為使用者生成大量行程和事件 ---
        # (邏輯與前版相同)
        self.stdout.write("🚚 Generating a massive amount of trip data (this will take some time)...")
        now = timezone.now()
        all_users_to_seed = [superuser, admin_user] + created_drivers
        for user in all_users_to_seed:
            user_groups = list(user.joined_groups.all())
            if not user_groups: continue
            for month_delta in range(4):
                for _ in range(random.randint(5, 10)):
                    trip_start_time = now - timedelta(days=month_delta * 30 + random.randint(1, 28), hours=random.randint(6, 20))
                    trip_end_time = trip_start_time + timedelta(hours=random.randint(2, 8), minutes=random.randint(10, 59))
                    trip = Trip.objects.create(trip_number=f"TRIP-{timezone.now().timestamp()}-{random.randint(1000, 9999)}", name=f"{trip_start_time.strftime('%Y-%m-%d')} {random.choice(['例行配送', '客戶急件'])}", group=random.choice(user_groups), device=random.choice(devices), personnel=user, start_time=trip_start_time, end_time=trip_end_time, total_mileage=random.uniform(80.0, 450.0))
                    num_events = random.randint(1, 8)
                    if random.random() < 0.2: num_events = random.randint(5, 12)
                    for _ in range(num_events):
                        event_time = trip_start_time + timedelta(minutes=random.randint(5, (trip_end_time - trip_start_time).seconds // 60 - 5))
                        AiVisionLog.objects.create(trip=trip, event=random.choice(scoring_standards), timestamp=event_time, event_details="模擬數據")
                    calculate_trip_score(trip.id)
        self.stdout.write(self.style.SUCCESS(f"✅ Trips generated and scored."))
        
        # --- 7. 建立系統與群組公告 ---
        self.stdout.write("📢 Creating announcements...")
        SystemAnnouncement.objects.create(announcement_number="SYS-2025-001", content="歡迎使用新版 MDG Pro 系統！", is_active=True)
        for group in groups:
            GroupAnnouncement.objects.create(group=group, publisher=admin_user, content=f"歡迎各位加入 {group.name}，請注意行車安全。")
        self.stdout.write(self.style.SUCCESS("✅ Announcements created."))

        # --- 8. 建立邀請碼 ---
        self.stdout.write("✉️ Creating invitation codes...")
        for group in groups:
            InvitationCode.objects.create(
                name=f"{group.name} 2025年Q4招募",
                group=group,
                created_by=admin_user,
                expires_at=timezone.now() + timedelta(days=90)
            )
        self.stdout.write(self.style.SUCCESS("✅ Invitation codes created."))

        self.stdout.write(self.style.SUCCESS("🎉 Final database seeding complete! Your system is ready for a full test drive."))