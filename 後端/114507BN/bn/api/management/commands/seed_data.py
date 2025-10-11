# 檔案路徑: api/management/commands/seed_data.py (最終版 - 為所有管理員生成資料)

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from faker import Faker
from api.models import (
    PersonnelProfile, Group, GroupMember, ScoringStandard, VehicleDevice,
    Trip, AiVisionLog, VideoRecord, GroupAnnouncement
)
from api.services import calculate_trip_score

# 初始化 Faker
fake = Faker('zh_TW')

class Command(BaseCommand):
    help = 'Seeds the database with a large, corporate-style set of test data for ALL users including superuser.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🚀 Starting final database seeding process..."))

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
        VideoRecord.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✅ Old data cleaned up."))

        # --- 2. 建立評分標準 ---
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
        
        # --- 3. 建立使用者、Profile 和車機 ---
        self.stdout.write("👤 Creating a large number of users and devices...")
        
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser:
                raise User.DoesNotExist
            self.stdout.write(f"   - Using superuser: {superuser.username} as a creator.")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ No superuser found. Please run 'python manage.py createsuperuser' first."))
            return

        admin_user, _ = User.objects.get_or_create(username='joywu', defaults={'first_name': '佳憲', 'last_name': '吳', 'email': 'joywu@example.com'})
        admin_user.set_password('admin1234')
        admin_user.save()
        PersonnelProfile.objects.get_or_create(user=admin_user, defaults={'personnel_number': 'T1056017'})
        self.stdout.write(f"   - Created admin: joywu (password: admin1234)")
        
        created_drivers = []
        for i in range(1, 21):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f'driver{i:02d}'
            user, _ = User.objects.get_or_create(username=username, defaults={'first_name': first_name, 'last_name': last_name, 'email': f'{username}@example.com'})
            user.set_password('driver1234')
            user.save()
            PersonnelProfile.objects.get_or_create(user=user, defaults={'personnel_number': f'D{1000+i}'})
            created_drivers.append(user)
        self.stdout.write(f"   - Created {len(created_drivers)} drivers (password: driver1234)")

        devices = [VehicleDevice.objects.get_or_create(device_number=f'MDG-TRUCK-{i:02d}', defaults={'vehicle_type': '貨車', 'activation_date': timezone.now().date()})[0] for i in range(1, 6)]
        self.stdout.write(self.style.SUCCESS(f"✅ Users and devices created."))

        # --- 4. 建立 3 個群組並分配成員 ---
        self.stdout.write("🏢 Creating 3 groups and assigning members...")
        group_names = ['北區-A組 (長途)', '中區-B組 (市區)', '南區-C組 (急件)']
        groups = []
        for i, name in enumerate(group_names):
            group, _ = Group.objects.get_or_create(name=name, defaults={'group_number': f'TEAM-{chr(65+i)}', 'created_by': superuser})
            groups.append(group)
        
        # 將 Superuser 和 Admin 都加入所有群組
        for group in groups:
             GroupMember.objects.get_or_create(group=group, user=superuser, defaults={'role': 'ADMIN'})
             GroupMember.objects.get_or_create(group=group, user=admin_user, defaults={'role': 'ADMIN'})

        for i, user in enumerate(created_drivers):
            GroupMember.objects.get_or_create(group=groups[i % len(groups)], user=user, defaults={'role': 'MEMBER'})
        self.stdout.write(self.style.SUCCESS("✅ Groups created and members assigned."))

        # --- 5. 為使用者生成大量行程和事件 ---
        self.stdout.write("🚚 Generating a massive amount of trip data (this will take some time)...")
        now = timezone.now()

        # ▼▼▼【核心修改】將 superuser 也加入到行程生成列表中 ▼▼▼
        all_users_to_seed = [superuser, admin_user] + created_drivers
        total_trips = 0

        for user in all_users_to_seed:
            self.stdout.write(f"   - Generating data for {user.username}...")
            user_groups = list(user.joined_groups.all())
            if not user_groups: 
                self.stdout.write(self.style.WARNING(f"     -> Skipping {user.username}, not in any groups."))
                continue
            
            for month_delta in range(4):
                for _ in range(random.randint(5, 10)):
                    trip_start_time = now - timedelta(days=month_delta * 30 + random.randint(1, 28), hours=random.randint(6, 20))
                    trip_end_time = trip_start_time + timedelta(hours=random.randint(2, 8), minutes=random.randint(10, 59))
                    
                    trip = Trip.objects.create(
                        trip_number=f"TRIP-{timezone.now().timestamp()}-{random.randint(1000, 9999)}",
                        name=f"{trip_start_time.strftime('%Y-%m-%d')} {random.choice(['例行配送', '客戶急件', '跨區調度', '倉儲補貨'])}",
                        group=random.choice(user_groups), device=random.choice(devices), personnel=user,
                        start_time=trip_start_time, end_time=trip_end_time, total_mileage=random.uniform(80.0, 450.0)
                    )
                    total_trips += 1

                    is_bad_trip = random.random() < 0.2
                    num_events = random.randint(5, 12) if is_bad_trip else random.randint(1, 8)
                    
                    bad_interval_time = None
                    if is_bad_trip:
                         bad_interval_time = trip_start_time + timedelta(minutes=random.randint(15, (trip_end_time - trip_start_time).seconds // 60 - 30))

                    for i in range(num_events):
                        if is_bad_trip and i < 4:
                            event_time = bad_interval_time + timedelta(minutes=random.randint(0, 14))
                        else:
                            event_time = trip_start_time + timedelta(minutes=random.randint(5, (trip_end_time - trip_start_time).seconds // 60 - 5))
                        
                        AiVisionLog.objects.create(trip=trip, event=random.choice(scoring_standards), timestamp=event_time, event_details="模擬數據")
                    
                    calculate_trip_score(trip.id)
        
        self.stdout.write(self.style.SUCCESS(f"✅ {total_trips} trips generated and scored."))
        self.stdout.write(self.style.SUCCESS("🎉 Database seeding complete! You now have a rich dataset for testing."))