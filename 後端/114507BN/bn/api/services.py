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


# (以下所有函式維持不變，為了完整性，我將它們全部提供)

def calculate_trip_score(trip_id: int):
    try:
        trip = Trip.objects.get(id=trip_id)
        if not trip.start_time or not trip.end_time: return None
    except Trip.DoesNotExist: return None
    events = AiVisionLog.objects.filter(trip=trip).select_related('event')
    if not events.exists():
        trip.in_car_score, trip.out_car_score, trip.score = 100, 100, 100
        trip.ai_suggestion = "本次行程表現良好，未偵測到任何危險駕駛行為。請繼續保持！"
        trip.save(update_fields=['in_car_score', 'out_car_score', 'score', 'ai_suggestion'])
        return { "final_score": 100, "in_car_score": 100, "out_car_score": 100 }
    intervals, current_time = [], trip.start_time
    while current_time < trip.end_time:
        interval_end = current_time + timedelta(minutes=15)
        intervals.append({'start': current_time, 'end': interval_end, 'in_car_deductions': 0, 'out_car_deductions': 0})
        current_time = interval_end
    for event in events:
        for interval in intervals:
            if interval['start'] <= event.timestamp < interval['end']:
                category, deduction = event.event.event_number[0].upper(), event.event.deduction_points or 0
                if category == 'A': interval['in_car_deductions'] += deduction
                elif category == 'B': interval['out_car_deductions'] += deduction
                break
    in_car_interval_scores = [max(0, 100 - i['in_car_deductions']) for i in intervals if i['in_car_deductions'] > 0]
    out_car_interval_scores = [max(0, 100 - i['out_car_deductions']) for i in intervals if i['out_car_deductions'] > 0]
    def _get_final_category_score(scores: list):
        if not scores: return 100.0
        if any(s < 60 for s in scores): return float(min(scores))
        else: return sum(scores) / len(scores)
    final_in_car_score, final_out_car_score = _get_final_category_score(in_car_interval_scores), _get_final_category_score(out_car_interval_scores)
    final_score = (final_in_car_score + final_out_car_score) / 2
    ai_suggestion_text = generate_ai_suggestion(trip_id)
    trip.in_car_score, trip.out_car_score, trip.score, trip.ai_suggestion = final_in_car_score, final_out_car_score, final_score, ai_suggestion_text
    trip.save(update_fields=['in_car_score', 'out_car_score', 'score', 'ai_suggestion'])
    return {"final_score": final_score, "in_car_score": final_in_car_score, "out_car_score": final_out_car_score, "ai_suggestion": ai_suggestion_text}

def is_driver_on_active_trip(user: User) -> bool:
    return Trip.objects.filter(personnel=user, end_time__isnull=True).exists()

def generate_ai_suggestion(trip_id: int) -> str:
    if not gemini_model: return "系統設定錯誤：Vertex AI 初始化失敗。"
    try:
        events = AiVisionLog.objects.filter(trip_id=trip_id).order_by('timestamp')
        if not events.exists(): return "本次行程表現良好，未偵測到明顯的危險駕駛行為。"
    except Exception: return "系統錯誤：查詢行程事件時發生錯誤。"
    
    event_summary = "\n".join([f"- {log.timestamp.strftime('%H:%M:%S')} | {log.event.description} (細節: {log.event.details})" for log in events])
    full_prompt = f"""
<role>
你是一位頂尖的智慧駕駛安全分析師「吾仙」。
</role>
<input_data>
行程危險駕駛事件清單:
{event_summary}
</input_data>
<task>
根據紀錄，遵循 Markdown 模板生成一份完整的報告。
</task>
<output_template>
### MDG Pro 行程安全分析報告
**行程總結與風險評估：**
[1-2 句話總結主要風險]
**主要風險事件分析：**
* **[風險類型一]**：[描述風險嚴重性]
    * 偵測記錄：[列出事件]
**具體改善建議：**
1.  **[針對風險一的建議]**：[提供建議]
**結語：**
持續關注駕駛細節，是確保行車安全的關鍵。
</output_template>
"""
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