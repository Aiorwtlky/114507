# api/services.py (Hugging Face - Llama-3 8B 高速版)

import os
from datetime import timedelta
from dotenv import load_dotenv
from django.contrib.auth.models import User
from .models import Trip, AiVisionLog

# 匯入 Hugging Face 相關套件
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

# =============================================================================
# 0. 初始化設定 (Initialization)
# =============================================================================
load_dotenv()

# ▼▼▼【修改 1】更新為高速、高效的 Llama-3 8B 模型 ▼▼▼
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
hf_client = None

try:
    print("=====================================================================")
    print("✅ 正在嘗試連線到 Hugging Face Inference API...")
    
    hf_token = os.environ.get('HUGGINGFACE_API_TOKEN')
    if not hf_token:
        raise ValueError("環境變數 'HUGGINGFACE_API_TOKEN' 未設定，請在 .env 檔案中新增。")

    hf_client = InferenceClient(token=hf_token)
    
    print(f"✅ Hugging Face Client 連線成功。")
    print(f"   - 將使用高速模型: {MODEL_ID}")
    print("=====================================================================")

except (ValueError, Exception) as e:
    print(f"❌ Hugging Face 初始化失敗: {e}")
    print("警告：AI 相關功能將無法運作。")


# =============================================================================
# 1. 行程分數計算 (Trip Scoring) - 此函式無需修改
# =============================================================================
def calculate_trip_score(trip_id: int):
    # (此函式內容與之前完全相同，無需修改，為了簡潔已省略)
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

# =============================================================================
# 2. AI 建議生成 (Llama-3 版本)
# =============================================================================
def generate_ai_suggestion(trip_id: int) -> str:
    if not hf_client: 
        return "系統設定錯誤：Hugging Face 初始化失敗，無法生成 AI 建議。"
    try:
        events = AiVisionLog.objects.filter(trip_id=trip_id).order_by('timestamp')
        if not events.exists(): 
            return "本次行程表現良好，未偵測到明顯的危險駕駛行為。"
    except Exception as e:
        print(f"[AI Service - Suggestion] 查詢行程事件錯誤: {e}")
        return "系統錯誤：查詢行程事件時發生錯誤。"
    
    event_summary = "\n".join([f"- {log.timestamp.strftime('%H:%M:%S')} | {log.event.description} (細節: {log.event.details})" for log in events])
    
    # ▼▼▼【修改 2】建立符合 Llama-3 模型的 Prompt 格式 ▼▼▼
    system_prompt = "你是一位頂尖的智慧駕駛安全分析師「吾仙」。"
    user_prompt = f"""
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
    # Llama-3 的訊息格式
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        # 使用 chat_completion 方法，它能更好地處理多輪對話格式
        response = hf_client.chat_completion(
            messages=messages,
            model=MODEL_ID,
            max_tokens=1024,
        )
        # 提取回覆內容
        return response.choices[0].message.content.strip()
    except HfHubHTTPError as e:
        print(f"[AI Service - Suggestion] Hugging Face API 呼叫錯誤: {e}")
        return f"系統分析您本次行程有以下事件：\n{event_summary}\n\n建議您注意改善駕駛習慣。(AI 助理連線失敗)"
    except Exception as e:
        print(f"[AI Service - Suggestion] 未預期的錯誤: {e}")
        return "生成建議時發生未預期的錯誤。"


# =============================================================================
# 3. 聊天機器人回應 (Llama-3 版本)
# =============================================================================
def get_chatbot_response(chat_history: list) -> str:
    if not hf_client: 
        return "抱歉，助理系統目前無法連線，請稍後再試。"
    
    # ▼▼▼【修改 3】建立符合 Llama-3 模型的對話歷史 Prompt ▼▼▼
    system_prompt = """<persona>
你是「吾仙」，一個專為「吾駕仙」(My Driving God) 智慧交通系統服務的頂尖 AI 助理。
</persona>
<rules>
1.  **嚴守範圍**：你的所有回答都必須嚴格限制在「吾駕仙」系統功能、駕駛安全分析、交通法規與安全知識的範疇內。
2.  **拒絕無關問題**：當使用者提出任何與上述範圍無關的問題時，你必須且只能使用以下固定句式回答：「抱歉，這個問題超出了我作為吾駕仙交通助理的知識範圍。我可以協助您分析駕駛報告，或提供交通安全建議，請問有這方面的問題嗎？」
3.  **禁止自我揭露**：在任何情況下，都不能承認自己是 AI、語言模型或機器人。
</rules>
"""
    # 將您的歷史紀錄轉換為 Llama-3 的格式
    messages = [{"role": "system", "content": system_prompt}]
    for message in chat_history:
        role = message.get('role')
        content = message.get('content', '')
        # 將 'model' 角色轉換為 Llama-3 需要的 'assistant'
        if role == 'model':
            messages.append({"role": "assistant", "content": content})
        elif role == 'user':
            messages.append({"role": "user", "content": content})

    try:
        # 使用 chat_completion 方法
        response = hf_client.chat_completion(
            messages=messages,
            model=MODEL_ID,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except HfHubHTTPError as e:
        print(f"[AI Service - Chatbot] Hugging Face API 呼叫錯誤: {e}")
        return "抱歉，我現在好像遇到了一點技術問題，請您稍後再問我一次。"
    except Exception as e:
        print(f"[AI Service - Chatbot] 未預期的錯誤: {e}")
        return "處理您的請求時發生未預期的錯誤。"


# =============================================================================
# 4. 輔助函式 (Utility Functions) - 此函式無需修改
# =============================================================================
def is_driver_on_active_trip(user: User) -> bool:
    """檢查指定使用者當前是否有正在進行中的行程。"""
    return Trip.objects.filter(personnel=user, end_time__isnull=True).exists()