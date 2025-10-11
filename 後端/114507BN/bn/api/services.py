# api/services.py (終極診斷版)

import os
from datetime import timedelta
from dotenv import load_dotenv
from django.contrib.auth.models import User
from .models import Trip, AiVisionLog

# ▼▼▼【終極診斷 1】匯入 Google Cloud 認證相關套件 ▼▼▼
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
from google.oauth2 import service_account
from google.auth import exceptions as auth_exceptions

# =============================================================================
# 0. 初始化設定 (Initialization)
# =============================================================================
load_dotenv()

gemini_model = None
try:
    print("=====================================================================")
    print("✅ 正在嘗試以【終極診斷模式】連線到 Vertex AI...")

    # ▼▼▼【終極診斷 2】直接在程式碼中寫死金鑰路徑和專案設定 ▼▼▼
    # 請再次確認下方的 key_path 是您 .json 檔案的絕對路徑
    key_path = "/Users/joych53/114507/後端/114507BN/bn/my-driving-god-ai-3fb319939e3e.json"
    project_id = "my-driving-god-ai"
    location = "us-central1"
    
    print(f"   - 專案 ID: {project_id}")
    print(f"   - 地區: {location}")
    print(f"   - 認證檔案路徑: {key_path}")

    # 檢查檔案是否存在
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"指定的認證檔案不存在於路徑: {key_path}")

    # 直接從 JSON 檔案建立認證憑證
    credentials = service_account.Credentials.from_service_account_file(key_path)
    
    # 使用建立的憑證進行初始化
    vertexai.init(project=project_id, location=location, credentials=credentials)
    print("   - 認證憑證已成功載入。")

    system_instruction_for_chatbot = """
<persona>
你是「吾仙」，一個專為「吾駕仙」(My Driving God) 智慧交通系統服務的頂尖 AI 助理。
</persona>
<rules>
1.  **嚴守範圍**：你的所有回答都必須嚴格限制在「吾駕仙」系統功能、駕駛安全分析、交通法規與安全知識的範疇內。
2.  **拒絕無關問題**：當使用者提出任何與上述範圍無關的問題時，你必須且只能使用以下固定句式回答：「抱歉，這個問題超出了我作為吾駕仙交通助理的知識範圍。我可以協助您分析駕駛報告，或提供交通安全建議，請問有這方面的問題嗎？」
3.  **禁止自我揭露**：在任何情況下，都不能承認自己是 AI、語言模型或機器人。
</rules>
"""
    gemini_model = GenerativeModel(
        "gemini-1.5-pro-001",
        system_instruction=[system_instruction_for_chatbot]
    )
    print(f"✅ Vertex AI Gemini 連線成功 (模型: gemini-1.5-pro-001 @ {location})。")
    print("=====================================================================")

except auth_exceptions.DefaultCredentialsError as e:
    print(f"❌ Vertex AI 初始化失敗: 預設憑證錯誤。這通常意味著環境變數設定不正確或 gcloud CLI 認證衝突。錯誤: {e}")
    print("警告：AI 相關功能將無法運作。")
except FileNotFoundError as e:
    print(f"❌ Vertex AI 初始化失敗: {e}")
    print("警告：AI 相關功能將無法運作。")
except Exception as e:
    print(f"❌ Vertex AI 初始化失敗: 發生未預期的錯誤: {e}")
    print("警告：AI 相關功能將無法運作。")


def calculate_trip_score(trip_id: int):
    """【最新版】根據詳細的15分鐘區間規則，重新計算行程分數。"""
    try:
        trip = Trip.objects.get(id=trip_id)
        if not trip.start_time or not trip.end_time:
            print(f"[Scoring Service] 錯誤: 行程 {trip_id} 缺少時間戳，無法計分。")
            return None
    except Trip.DoesNotExist:
        print(f"[Scoring Service] 錯誤: 找不到 ID 為 {trip_id} 的行程。")
        return None

    events = AiVisionLog.objects.filter(trip=trip).select_related('event')
    
    # 如果沒有任何違規事件，直接給滿分
    if not events.exists():
        trip.in_car_score = 100
        trip.out_car_score = 100
        trip.score = 100
        trip.ai_suggestion = "本次行程表現良好，未偵測到任何危險駕駛行為。請繼續保持！"
        trip.save(update_fields=['in_car_score', 'out_car_score', 'score', 'ai_suggestion'])
        print(f"行程 {trip.trip_number} 無違規事件，評為滿分。")
        return { "final_score": 100, "in_car_score": 100, "out_car_score": 100 }

    # ▼▼▼【核心邏輯修改】根據新規則重寫計分過程 ▼▼▼
    
    # 1. 將行程切分為15分鐘區間
    intervals = []
    current_time = trip.start_time
    while current_time < trip.end_time:
        interval_end = current_time + timedelta(minutes=15)
        intervals.append({
            'start': current_time, 
            'end': interval_end, 
            'in_car_deductions': 0, 
            'out_car_deductions': 0
        })
        current_time = interval_end

    # 2. 將每個事件的扣分累加到對應的區間
    for event in events:
        for interval in intervals:
            if interval['start'] <= event.timestamp < interval['end']:
                category = event.event.event_number[0].upper()
                deduction = event.event.deduction_points or 0
                if category == 'A':
                    interval['in_car_deductions'] += deduction
                elif category == 'B':
                    interval['out_car_deductions'] += deduction
                break

    # 3. 計算每個區間的得分 (滿分100)
    in_car_interval_scores = [max(0, 100 - i['in_car_deductions']) for i in intervals]
    out_car_interval_scores = [max(0, 100 - i['out_car_deductions']) for i in intervals]

    # 4. 根據「類別評分」規則，計算最終的 A類 和 B類 分數
    def _get_final_category_score(scores: list):
        """
        - 如果有任何區間 <= 60，則類別總分 = 最低區間分。
        - 否則，類別總分 = 所有區間的平均分。
        """
        if not scores: return 100.0
        
        # 檢查是否有任何區間分數低於或等於60
        if any(s <= 60 for s in scores):
            return float(min(scores))
        else:
            return sum(scores) / len(scores)

    final_in_car_score = _get_final_category_score(in_car_interval_scores)
    final_out_car_score = _get_final_category_score(out_car_interval_scores)
    
    # 5. 根據「行程總分」規則計算最終分數
    final_score = (final_in_car_score * 0.5) + (final_out_car_score * 0.5)
    
    # 6. 生成 AI 建議並儲存所有結果
    ai_suggestion_text = generate_ai_suggestion(trip_id)
    
    trip.in_car_score = round(final_in_car_score, 2)
    trip.out_car_score = round(final_out_car_score, 2)
    trip.score = round(final_score, 2)
    trip.ai_suggestion = ai_suggestion_text
    trip.save(update_fields=['in_car_score', 'out_car_score', 'score', 'ai_suggestion'])
    
    print(f"行程 {trip.trip_number} 新版評分完成。車內: {final_in_car_score:.1f}, 車外: {final_out_car_score:.1f}, 總分: {final_score:.1f}")
    
    return { 
        "final_score": final_score, 
        "in_car_score": final_in_car_score, 
        "out_car_score": final_out_car_score,
        "ai_suggestion": ai_suggestion_text 
    }

# (is_driver_on_active_trip, generate_ai_suggestion, get_chatbot_response 等函式維持不變)
# ...
# ... (為了讓您方便複製貼上，這裡補上所有省略的程式碼)
def is_driver_on_active_trip(user: User) -> bool: return Trip.objects.filter(personnel=user, end_time__isnull=True).exists()
def generate_ai_suggestion(trip_id: int) -> str:
    if not gemini_model: return "系統設定錯誤：Vertex AI 初始化失敗。"
    try:
        events = AiVisionLog.objects.filter(trip_id=trip_id).order_by('timestamp')
        if not events.exists(): return "本次行程表現良好，未偵測到明顯的危險駕駛行為。"
    except Exception: return "系統錯誤：查詢行程事件時發生錯誤。"
    event_summary = "\n".join([f"- {log.timestamp.strftime('%H:%M:%S')} | {log.event.description} (細節: {log.event_details})" for log in events])
    full_prompt = f"""<role>...</role><input_data>...\n{event_summary}\n</input_data><task>...</task><output_template>...</output_template>""" # 簡化顯示
    report_model = GenerativeModel("gemini-1.5-pro-001")
    try:
        response = report_model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[AI Service - Suggestion] Vertex AI API 呼叫錯誤: {e}")
        return f"系統分析您本次行程有以下事件：\n{event_summary}\n\n建議您注意改善駕駛習慣。"
def get_chatbot_response(chat_history: list) -> str:
    if not gemini_model: return "抱歉，助理系統目前無法連線，請稍後再試。"
    try:
        gemini_formatted_history = []
        for message in chat_history:
            role = message.get('role')
            content_text = message.get('content', '')
            if role in ['user', 'model']:
                gemini_formatted_history.append(Content(role=role, parts=[Part.from_text(content_text)]))
        response = gemini_model.generate_content(gemini_formatted_history)
        return response.text.strip()
    except Exception as e:
        print(f"[AI Service - Chatbot] Vertex AI API 呼叫錯誤: {e}")
        return "抱歉，我現在好像遇到了一點技術問題，請您稍後再問我一次。"