# 檔案路徑: api/management/commands/seed_data.py

import random
import api.services  # 用於替換 AI 函式
from datetime import timedelta, datetime, time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from faker import Faker
from api.models import (
    PersonnelProfile, Group, GroupMember, ScoringStandard, VehicleDevice,
    Trip, AiVisionLog, GroupAnnouncement, SystemAnnouncement,
    ActivationCode, InvitationCode
)
from api.services import calculate_trip_score

fake = Faker('zh_TW')

# 設定目標日期：讓數據看起來像是在 2025/11/23 截止
TARGET_DATE = timezone.make_aware(datetime(2025, 11, 23, 23, 59, 59))

class Command(BaseCommand):
    help = '生成 MDG Pro 演示資料：包含 15 種情境式 AI 建議與指定人員名單'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # ==========================================
        # 🧠 智慧型擬真 AI 引擎 (Context-Aware Fake AI)
        # ==========================================
        self.stdout.write(self.style.WARNING("⚡️ 啟動智慧型模擬引擎：根據違規事件自動生成 15 種情境建議..."))
        
        def smart_fake_ai_suggestion(trip_id):
            # 1. 撈出這趟行程發生了什麼違規
            trip = Trip.objects.get(id=trip_id)
            logs = AiVisionLog.objects.filter(trip=trip)
            event_codes = [log.event.event_number for log in logs]
            
            # 2. 定義豐富的建議庫 (10種以上)
            suggestions = {
                # --- 優良 (無違規) ---
                'PERFECT_1': "本次行程駕駛行為優良，防禦性駕駛觀念極佳。在變換車道與過彎時的操作皆十分標準，請繼續保持。",
                'PERFECT_2': "行駛平穩，預判路況能力強。系統未偵測到任何風險事件，這是一趟完美的駕駛範例。",
                'PERFECT_3': "各項安全指標皆為滿分。在高速路段能保持適當車距，市區行駛禮讓行人，值得嘉許。",
                
                # --- 疲勞類 (A01, A02) ---
                'FATIGUE_MILD': "【疲勞警示】偵測到您有頻繁眨眼與打哈欠的徵兆。雖然尚未造成事故，但專注力已下降，強烈建議休息 15 分鐘。",
                'FATIGUE_SEVERE': "【高度危險】系統記錄到閉眼超過 3 秒！這極可能導致嚴重車禍。請務必立即駛入休息站，切勿疲勞駕駛。",
                'FATIGUE_NIGHT': "【夜間疲勞】深夜駕駛容易精神不濟，系統偵測到您的反應時間變慢。請開啟空調外循環或飲用提神飲料。",

                # --- 分心類 (A03, A04) ---
                'PHONE_USE': "【違規警示】行駛中偵測到使用手持裝置（手機）。這會使事故風險增加 4 倍，請使用免持裝置或語音助理。",
                'DISTRACTION_FACE': "【分心警示】視線頻繁離開前方路面（轉頭/低頭）。請將注意力集中在駕駛上，忽略車內干擾源。",
                
                # --- 危險駕駛類 (B01-B04) ---
                'RED_LIGHT': "【重大違規】偵測到闖紅燈行為！這不僅違反交通法規，更嚴重威脅路口安全。請嚴格遵守號誌。",
                'BRAKE': "【操作建議】急煞車次數過多。這顯示您與前車距離過近或觀察不足。請預留更多緩衝空間，提升乘客舒適度。",
                'LANE_CHANGE': "【變換車道】變換車道未提前使用方向燈。這容易造成後方來車誤判，請養成提早打燈的好習慣。",
                'SPEEDING': "【速度管理】部分路段車速過快。十次車禍九次快，請依照速限行駛，確保行車安全。",
                
                # --- 混合情境 ---
                'MIXED_BAD': "【綜合分析】本趟行程風險極高。同時偵測到分心使用手機與急煞車。這種組合極易導致追撞事故，請立即改善駕駛習慣。",
                'IMPROVING': "【進步鼓勵】雖然仍有少許瑕疵，但比起上週的紀錄，您的急煞車次數已明顯減少。請繼續維持這個進步趨勢。",
                'TRAFFIC_JAM': "【塞車路況】在走走停停的車流中，偵測到數次跟車過近。塞車時更應保持耐心與安全距離。"
            }

            # 3. 邏輯判斷：根據違規內容回傳對應建議
            if not event_codes:
                return f"【AI 綜合分析】{random.choice([suggestions['PERFECT_1'], suggestions['PERFECT_2'], suggestions['PERFECT_3']])}"
            
            if 'A01' in event_codes: return f"【AI 安全警示】{suggestions['FATIGUE_SEVERE']}"
            if 'A02' in event_codes: return f"【AI 安全警示】{suggestions['FATIGUE_MILD']}"
            if 'A03' in event_codes: return f"【AI 行為分析】{suggestions['PHONE_USE']}"
            if 'B01' in event_codes: return f"【AI 重大違規】{suggestions['RED_LIGHT']}"
            if 'B02' in event_codes: 
                if random.random() > 0.5: return f"【AI 駕駛建議】{suggestions['BRAKE']}"
                else: return f"【AI 綜合分析】{suggestions['MIXED_BAD']}"
            
            # 預設回傳
            return f"【AI 駕駛建議】根據大數據分析，建議您留意：{suggestions['LANE_CHANGE']}"

        # 強制替換 services.py 裡的函式
        api.services.generate_ai_suggestion = smart_fake_ai_suggestion
        # ==========================================

        self.stdout.write(self.style.SUCCESS(f"🚀 開始生成資料，截止日期：{TARGET_DATE.strftime('%Y-%m-%d')}"))

        # --- 1. 清理舊資料 ---
        self.stdout.write("🧹 清理資料庫...")
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

        # --- 2. 基礎設定 ---
        ActivationCode.objects.create(code="DEMO-2025", notes="演示專用", max_uses=999)
        
        standards_config = [
            ('A01', '閉眼疲勞駕駛(>3s)', 40), ('A02', '頻繁眨眼/打哈欠', 25),
            ('A03', '使用手持裝置', 20), ('A04', '分心/未看前方', 15),
            ('B01', '闖紅燈', 30), ('B02', '急煞車', 10),
            ('B03', '未禮讓行人', 20), ('B04', '變換車道未打燈', 15),
        ]
        standards = [ScoringStandard.objects.create(event_number=c, description=d, deduction_points=p) for c, d, p in standards_config]

        # Superuser
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            superuser = User.objects.create_superuser('admin', 'admin@demo.com', 'admin1234')
            PersonnelProfile.objects.create(user=superuser, personnel_number='ADMIN-001')

        # 建立大量車機
        devices = []
        for i in range(1, 61): # 60台車
            d_prefix = "YC" if i <= 40 else ("HAVI" if i <= 55 else "NTUB")
            dev, _ = VehicleDevice.objects.get_or_create(
                device_number=f'MDG-{d_prefix}-{i:03d}',
                defaults={'vehicle_type': '貨運曳引車' if i <= 40 else '公務車', 'activation_date': (TARGET_DATE - timedelta(days=365)).date()}
            )
            devices.append(dev)

        # --- 3. 定義公司結構與指定名單 ---
        self.stdout.write("🏢 建立公司與人員...")
        
        companies = [
            {
                'id': 'YC', 
                'name': '昱成交通有限公司', 
                'code': 'YC-TRANS', 
                'desc': '全台最大冷鏈物流與危險品運輸車隊',
                'trip_freq': 0.85, # 資料量最大
                'users': [
                    {'u': 'yc_boss', 'n': '王大成', 'r': 'ADMIN', 'title': '董事長'},
                    # --- 關鍵角色 (有故事性) ---
                    {'u': 'yc_driver1', 'n': '林阿發', 'r': 'MEMBER', 'title': '資深駕駛', 'archetype': 'IMPROVING'}, # 進步型
                    {'u': 'yc_driver2', 'n': '陳國榮', 'r': 'MEMBER', 'title': '模範駕駛', 'archetype': 'PERFECT'},   # 完美型
                    {'u': 'yc_driver3', 'n': '張建宏', 'r': 'MEMBER', 'title': '大貨車駕駛', 'archetype': 'RISKY'},  # 危險型
                    # --- 填充角色 ---
                    {'u': 'yc_driver4', 'n': '劉德華', 'r': 'MEMBER', 'title': '約聘駕駛', 'archetype': 'AVERAGE'},
                    {'u': 'yc_driver5', 'n': '張學友', 'r': 'MEMBER', 'title': '聯結車駕駛', 'archetype': 'AVERAGE'},
                    {'u': 'yc_driver6', 'n': '郭富城', 'r': 'MEMBER', 'title': '夜班駕駛', 'archetype': 'AVERAGE'},
                ]
            },
            {
                'id': 'HAVI', 
                'name': 'HAVI Groups', 
                'code': 'HAVI-TW', 
                'desc': '全球供應鏈管理領導品牌',
                'trip_freq': 0.5, # 資料量中等
                'users': [
                    {'u': 'havi_manager', 'n': '李經理', 'r': 'ADMIN', 'title': '運務經理'},
                    {'u': 'havi_driver1', 'n': '王小明', 'r': 'MEMBER', 'title': '物流士', 'archetype': 'AVERAGE'},
                    {'u': 'havi_driver2', 'n': '趙子龍', 'r': 'MEMBER', 'title': '物流士', 'archetype': 'GOOD'},
                ]
            },
            {
                'id': 'NTUB', 
                'name': '台北商業大學資訊管理系', 
                'code': 'NTUB-IM', 
                'desc': '智慧交通產學合作實驗室',
                'trip_freq': 0.3, # 資料量較少
                'users': [
                    # 指定名單：組長吳佳憲
                    {'u': 'joy_wu', 'n': '吳佳憲', 'r': 'ADMIN', 'title': '專案組長'}, 
                    # 指定名單：組員
                    {'u': 'guan_wen', 'n': '李冠彣', 'r': 'MEMBER', 'title': '技術開發', 'archetype': 'GOOD'},
                    {'u': 'ting_yi', 'n': '皇庭毅', 'r': 'MEMBER', 'title': '系統分析', 'archetype': 'AVERAGE'},
                    {'u': 'ting_xuan', 'n': '陳廷軒', 'r': 'MEMBER', 'title': '測試工程師', 'archetype': 'IMPROVING'},
                ]
            }
        ]

        # --- 4. 實作使用者與群組 ---
        user_map = {} 
        group_map = {} 

        for comp in companies:
            group = Group.objects.create(
                group_number=comp['code'], name=comp['name'], 
                description=comp['desc'], created_by=superuser
            )
            group_map[comp['id']] = group

            for u_data in comp['users']:
                full_name = u_data['n']
                last_name = full_name[0]
                first_name = full_name[1:]

                user = User.objects.create_user(
                    username=u_data['u'], email=f"{u_data['u']}@demo.com", 
                    password='password123', first_name=first_name, last_name=last_name
                )
                
                PersonnelProfile.objects.create(
                    user=user, 
                    personnel_number=f"EMP-{random.randint(1000,9999)}",
                    license_type='職業聯結車' if 'driver' in u_data['u'] else '普通小型車',
                    gender='MALE', 
                    phone=f"09{random.randint(10000000, 99999999)}",
                    driving_experience=random.randint(1, 20)
                )
                
                GroupMember.objects.create(group=group, user=user, role=u_data['r'])
                user.archetype = u_data.get('archetype', 'AVERAGE')
                user_map[u_data['u']] = user

                # 建立管理者相關內容
                if u_data['r'] == 'ADMIN':
                    group.created_by = user
                    group.save()
                    GroupAnnouncement.objects.create(
                        group=group, publisher=user, is_active=True,
                        content=f"<h3>{comp['name']} 系統公告</h3><p>歡迎 {u_data['n']} 帶領團隊加入 MDG Pro。</p>"
                    )
                    InvitationCode.objects.create(
                        name=f"{group.name} 內部邀請", group=group, created_by=user,
                        expires_at=timezone.now() + timedelta(days=30)
                    )

        # --- 5. 生成大量行程數據 ---
        self.stdout.write("🚚 正在生成行程數據...")

        DAYS_BACK = 90 
        start_date_limit = TARGET_DATE - timedelta(days=DAYS_BACK)

        for day_offset in range(DAYS_BACK + 1):
            current_day = start_date_limit + timedelta(days=day_offset)
            progress = day_offset / DAYS_BACK 

            for comp in companies:
                group = group_map[comp['id']]
                daily_trip_chance = comp['trip_freq']

                for u_data in comp['users']:
                    if u_data['r'] == 'ADMIN': continue 
                    
                    user = user_map[u_data['u']]
                    if random.random() > daily_trip_chance: continue

                    # 昱成每天 2-4 趟，其他 1-2 趟
                    trips_today = random.randint(2, 4) if comp['id'] == 'YC' else random.randint(1, 2)

                    for t in range(trips_today):
                        # 時間設定
                        trip_start = current_day.replace(hour=random.randint(7, 20), minute=random.randint(0, 59))
                        trip_start += timedelta(hours=t*3)
                        if trip_start > TARGET_DATE: continue
                        
                        duration = random.randint(30, 180)
                        trip_end = trip_start + timedelta(minutes=duration)

                        trip = Trip.objects.create(
                            trip_number=f"TR-{int(trip_start.timestamp())}-{random.randint(100,999)}",
                            name=f"{u_data['n']} - {trip_start.strftime('%m/%d')} {random.choice(['北高配送', '區域巡迴', '急件專送', '客戶拜訪'])}",
                            group=group, device=random.choice(devices), personnel=user,
                            start_time=trip_start, end_time=trip_end,
                            total_mileage=random.uniform(20, 250)
                        )

                        # === 根據 Archetype 生成違規 ===
                        archetype = getattr(user, 'archetype', 'AVERAGE')
                        num_events = 0
                        event_pool = standards

                        if archetype == 'PERFECT':
                            if random.random() < 0.05: num_events = 1 # 極少違規
                        
                        elif archetype == 'RISKY':
                            # 危險駕駛：多違規，且容易出現疲勞(A01)或手機(A03)
                            num_events = random.randint(3, 7)
                            event_pool = [s for s in standards if s.event_number in ['A01', 'A02', 'A03', 'B02']]
                        
                        elif archetype == 'IMPROVING':
                            # 進步型：隨時間減少違規
                            risk_factor = 1.0 - progress 
                            if random.random() < (risk_factor * 0.8):
                                num_events = random.randint(1, 4)
                        
                        else: # AVERAGE
                            if random.random() < 0.25: num_events = random.randint(1, 2)

                        if num_events > 0:
                            for _ in range(num_events):
                                evt = random.choice(event_pool)
                                e_time = trip_start + timedelta(minutes=random.randint(5, duration-5))
                                AiVisionLog.objects.create(
                                    trip=trip, event=evt, timestamp=e_time,
                                    event_details="模擬偵測事件", confidence_score=random.uniform(0.85, 0.99)
                                )

                        # 計算分數 (自動觸發智慧型假 AI)
                        calculate_trip_score(trip.id)

        self.stdout.write(self.style.SUCCESS("✅ 行程資料生成完畢。"))

        # --- 6. 系統公告 ---
        SystemAnnouncement.objects.create(announcement_number="SYS-001", content="系統維護通知：11/25 凌晨將進行升級。", is_active=True)
        
        self.stdout.write(self.style.SUCCESS("🎉 資料庫重置完成！"))
        self.stdout.write(self.style.WARNING("=========================================="))
        self.stdout.write(self.style.WARNING("請使用以下帳號登入 (密碼: password123):"))
        self.stdout.write(self.style.WARNING("1. 北商大資管 (Admin): joy_wu"))
        self.stdout.write(self.style.WARNING("2. 昱成交通 (Admin): yc_boss"))
        self.stdout.write(self.style.WARNING("3. HAVI Groups (Admin): havi_manager"))
        self.stdout.write(self.style.WARNING("=========================================="))