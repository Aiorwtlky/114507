from django.core.management.base import BaseCommand
from api.models import ScoringStandard

class Command(BaseCommand):
    help = '初始化 MDG Pro 的評分標準 (A類與B類)'

    def handle(self, *args, **kwargs):
        # 根據您的截圖定義標準資料
        standards = [
            # A類：車內評分
            {'code': 'A01', 'desc': '重度疲勞 (閉眼5秒以上)', 'points': 40},
            {'code': 'A02', 'desc': '中度疲勞 (閉眼3-5秒)', 'points': 30},
            {'code': 'A03', 'desc': '使用手機', 'points': 15},
            {'code': 'A04', 'desc': '臉部離開', 'points': 40},
            
            # B類：車外評分
            {'code': 'B01', 'desc': '切換車道未打方向燈', 'points': 15},
            {'code': 'B02', 'desc': '轉彎未打方向燈', 'points': 15},
            {'code': 'B03', 'desc': '未保持適當車距', 'points': 15},
        ]

        self.stdout.write("正在初始化評分標準...")

        for item in standards:
            # 使用 update_or_create，如果已存在就更新，不存在就建立
            obj, created = ScoringStandard.objects.update_or_create(
                event_number=item['code'],
                defaults={
                    'description': item['desc'],
                    'deduction_points': item['points'],
                    'is_active': True
                }
            )
            action = "建立" if created else "更新"
            self.stdout.write(f"- {action}: {item['code']} {item['desc']} (-{item['points']}分)")

        self.stdout.write(self.style.SUCCESS("✅ 評分標準初始化完成！"))