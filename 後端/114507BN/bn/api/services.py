# api/services.py (最終優化版)

import os
from datetime import timedelta
from dotenv import load_dotenv
from django.contrib.auth.models import User
from .models import Trip, AiVisionLog

import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
from google.oauth2 import service_account
from google.auth import exceptions as auth_exceptions

# =============================================================================
# 0. 初始化設定 (Initialization)
# =============================================================================
load_dotenv()

# --- 全域變數 ---
gemini_model = None

# --- 優化後的系統指令 (System Prompts) ---

# 1. 用於 AI 客服的系統指令
SYSTEM_INSTRUCTION_FOR_CHATBOT = """
<persona>
你是「吾仙」，一個專為「吾駕仙」(My Driving God) 智慧交通系統服務的頂尖 AI 助理。你的語氣必須總是保持冷靜、專業、且帶有同理心。
</persona>
<rules>
1.  **嚴守知識範圍**：你的所有回答都必須嚴格限制在「吾駕仙」系統的操作功能、駕駛安全數據分析、台灣的交通法規與安全知識的範疇內。
2.  **優雅地拒絕**：當使用者提出任何與上述範圍無關的問題時（例如：聊天、問天氣、寫詩），你必須且只能使用以下固定句式回答：「抱歉，這個問題超出了我作為吾駕仙交通助理的知識範圍。我可以協助您分析駕駛報告，或提供交通安全建議，請問有這方面的問題嗎？」
3.  **禁止自我揭露**：在任何情況下，都不能承認自己是 AI、語言模型或機器人。你是「吾仙」，是這個系統的一部分。
4.  **清晰簡潔**：回答應盡量簡潔、清晰、條理分明。使用正體中文（繁體中文）。
5.  **引導式提問**：如果使用者的問題模糊不清，你應主動提出澄清性的問題，以更好地理解他們的需求。
</rules>
"""

# 2. 用於產生行程建議的系統指令
SYSTEM_INSTRUCTION_FOR_SUGGESTION = """
<persona>
你是一位專業的駕駛安全分析師。你的任務是根據一份危險駕駛事件的清單，為駕駛員提供一份簡潔、專業、且具有建設性的總結報告。你的語氣必須是鼓勵性的，而非指責性的。
</persona>
<task>
你的報告必須嚴格遵循以下三個段落的結構：
1.  **總體評價**：用一句話，對本次行程的整體安全表現做一個總結。
2.  **關鍵改善項目**：以點列式 (bullet points) 的方式，列出本次行程中最需要注意的 2 到 3 個關鍵危險行為。每個項目都應包含「事件類型」和「發生時間」。
3.  **具體建議**：提供一個最重要、最具有行動性的駕駛建議，幫助駕駛員在下次行程中避免類似的錯誤。
</task>
<rules>
1.  **數據驅動**：你的所有分析都必須基於提供的事件清單，絕不能憑空捏造。
2.  **聚焦重點**：如果事件過多，請專注於最嚴重（扣分最高）或最頻繁發生的事件類型。
3.  **正向激勵**：報告結尾應帶有鼓勵性的話語。
4.  **格式精確**：嚴格按照「總體評價」、「關鍵改善項目」、「具體建議」的順序和格式輸出。使用正體中文（繁體中文）。
</rules>
"""

# --- Vertex AI 初始化 ---
try:
    # 從 .env 檔案讀取設定
    key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    if not all([key_path, project_id, location]):
        raise ValueError("環境變數 GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT_ID, GOOGLE_CLOUD_LOCATION 未完整設定。")

    if not os.path.exists(key_path):
        raise FileNotFoundError(f"指定的認證檔案不存在於路徑: {key_path}")

    credentials = service_account.Credentials.from_service_account_file(key_path)
    vertexai.init(project=project_id, location=location, credentials=credentials)

    # 初始化一個共用的 Gemini 模型實例
    gemini_model = GenerativeModel(
        "gemini-1.5-pro-preview-0409",
        system_instruction=[SYSTEM_INSTRUCTION_FOR_CHATBOT] # 預設使用客服的指令
    )
    print("✅ Vertex AI Gemini 服務已成功初始化。")

except Exception as e:
    print(f"❌ Vertex AI 初始化失敗: {e}")
    print("警告：所有 AI 相關功能將無法運作。")


# =============================================================================
# 1. 核心服務函式 (Core Service Functions)
# =============================================================================

def calculate_trip_score(trip_id: int):
    # ... (此函式邏輯完全正確，維持不變) ...
    try:
        trip = Trip.objects.get(id=trip_id)
        if not trip.start_time or not trip.end_time:
            return None
    except Trip.DoesNotExist:
        return None

    events = AiVisionLog.objects.filter(trip=trip).select_related('event')
    
    if not events.exists():
        trip.in_car_score = 100
        trip.out_car_score = 100
        trip.score = 100
        trip.ai_suggestion = "本次行程表現良好，未偵測到任何危險駕駛行為。請繼續保持！"
        trip.save(update_fields=['in_car_score', 'out_car_score', 'score', 'ai_suggestion'])
        return { "final_score": 100, "in_car_score": 100, "out_car_score": 100 }

    intervals = []
    current_time = trip.start_time
    while current_time < trip.end_time:
        interval_end = current_time + timedelta(minutes=15)
        intervals.append({'start': current_time, 'end': interval_end, 'in_car_deductions': 0, 'out_car_deductions': 0})
        current_time = interval_end

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

    in_car_interval_scores = [max(0, 100 - i['in_car_deductions']) for i in intervals]
    out_car_interval_scores = [max(0, 100 - i['out_car_deductions']) for i in intervals]

    def _get_final_category_score(scores: list):
        if not scores: return 100.0
        if any(s <= 60 for s in scores):
            return float(min(scores))
        else:
            return sum(scores) / len(scores)

    final_in_car_score = _get_final_category_score(in_car_interval_scores)
    final_out_car_score = _get_final_category_score(out_car_interval_scores)
    final_score = (final_in_car_score * 0.5) + (final_out_car_score * 0.5)
    
    ai_suggestion_text = generate_ai_suggestion(trip_id)
    
    trip.in_car_score = round(final_in_car_score, 2)
    trip.out_car_score = round(final_out_car_score, 2)
    trip.score = round(final_score, 2)
    trip.ai_suggestion = ai_suggestion_text
    trip.save(update_fields=['in_car_score', 'out_car_score', 'score', 'ai_suggestion'])
    
    return { "final_score": final_score, "in_car_score": final_in_car_score, "out_car_score": final_out_car_score, "ai_suggestion": ai_suggestion_text }


def is_driver_on_active_trip(user: User) -> bool:
    # ... (此函式邏輯完全正確，維持不變) ...
    return Trip.objects.filter(personnel=user, end_time__isnull=True).exists()


def generate_ai_suggestion(trip_id: int) -> str:
    """【優化版】使用統一的 Gemini 模型和更強大的 Prompt 來生成行程建議。"""
    if not gemini_model:
        return "系統設定錯誤：Vertex AI 初始化失敗。"
        
    try:
        events = AiVisionLog.objects.filter(trip_id=trip_id).order_by('timestamp')
        if not events.exists():
            return "本次行程表現良好，未偵測到明顯的危險駕駛行為。"
    except Exception:
        return "系統錯誤：查詢行程事件時發生錯誤。"
        
    event_summary = "\n".join([f"- {log.timestamp.strftime('%H:%M:%S')} | {log.event.description} (細節: {log.event_details})" for log in events])
    
    # 組合最終的 Prompt
    full_prompt = f"{SYSTEM_INSTRUCTION_FOR_SUGGESTION}\n\n[TRIP DATA]\n{event_summary}\n[/TRIP DATA]"
    
    # ▼▼▼【核心修正】移除錯誤的 report_model，改用正確的全域 gemini_model ▼▼▼
    try:
        # 由於此任務的指令與客服不同，我們在呼叫時傳入一次性的 system_instruction
        response = gemini_model.generate_content(
            full_prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"[AI Service - Suggestion] Vertex AI API 呼叫錯誤: {e}")
        return f"系統分析您本次行程有以下事件：\n{event_summary}\n\n建議您注意改善駕駛習慣。"


def get_chatbot_response(chat_history: list) -> str:
    """【優化版】使用統一的 Gemini 模型處理聊天。"""
    if not gemini_model:
        return "抱歉，助理系統目前無法連線，請稍後再試。"
        
    try:
        # 將傳入的對話歷史轉換為 Gemini SDK 需要的格式
        gemini_formatted_history = []
        for message in chat_history:
            role = message.get('role')
            content_text = message.get('content', '')
            if role in ['user', 'model']:
                gemini_formatted_history.append(Content(role=role, parts=[Part.from_text(content_text)]))
        
        # 直接使用預設了客服指令的 gemini_model 進行對話
        response = gemini_model.generate_content(gemini_formatted_history)
        return response.text.strip()
    except Exception as e:
        print(f"[AI Service - Chatbot] Vertex AI API 呼叫錯誤: {e}")
        return "抱歉，我現在好像遇到了一點技術問題，請您稍後再問我一次。"