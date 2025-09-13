# api/services.py
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from django.contrib.auth.models import User
from .models import Trip, AiVisionLog

# --- 初始化設定 (Initialization) ---
# 將初始化程式碼放在檔案頂部，讓整個模組共用一個 client 實例，更有效率
# --------------------------------------------------------------------------
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
client = None
if HF_TOKEN:
    # 我們使用 Hugging Face 官方的推論端點
    client = InferenceClient(token=HF_TOKEN)
else:
    # 提醒開發者在伺服器啟動時，Token 未設定
    print("警告：未在 .env 檔案中找到 HF_TOKEN。AI 相關功能將無法運作。")


# =============================================================================
# 邏輯一：行程結束後的「AI 總結報告產生器」
# =============================================================================
def generate_ai_suggestion(trip_id: int) -> str:
    """
    (自動化、單向任務)
    根據單趟行程的所有危險事件，生成一份正式、客觀的駕駛行為改善建議報告。
    這份報告將被儲存到資料庫中，作為該行程的最終總結。
    """
    if not client:
        return "系統設定錯誤：Hugging Face API Token 未配置。"

    try:
        trip = Trip.objects.get(id=trip_id)
        events = AiVisionLog.objects.filter(trip=trip)
    except Trip.DoesNotExist:
        return "系統錯誤：找不到對應的行程資料。"

    if not events.exists():
        return "本次行程表現良好，未偵測到明顯的危險駕駛行為。請繼續保持安全駕駛。"

    # 1. 組合一份清晰、條列式的事件摘要，讓 AI 更容易理解
    event_summary_parts = []
    for event_log in events:
        event_summary_parts.append(f"- 事件：{event_log.event.description}，細節：{event_log.event_details}")
    event_summary = "\n".join(event_summary_parts)

    # 2. 撰寫一份專為「報告生成」任務設計的、結構化的 Prompt
    system_prompt = "你是一位專業的智慧駕駛安全分析師，名叫「吾仙」。你的任務是根據一份危險駕駛事件的清單，撰寫一份客觀、專業、且具有建設性的駕駛行為改善建議報告。請避免口語化，並以條列式呈現重點。"
    user_prompt = f"""
請分析以下這趟行程的危險駕駛事件清單，並生成一份改善建議報告：

【危險事件清單】
{event_summary}

請在報告中條列出主要的風險點，並針對每個風險點提供具體的改善建議。
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # 3. 呼叫 AI 模型並回傳結果
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-14B-Instruct",
            messages=messages,
            max_tokens=300,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI Service - Suggestion] 遠端 API 呼叫錯誤: {e}")
        return f"系統分析您本次行程有以下事件：\n{event_summary}\n\n建議您注意改善駕駛習慣，確保行車安全。"

# =============================================================================
# 邏輯二：前端 AI 助理的「即時對話回應器」
# =============================================================================
def get_chatbot_response(chat_history: list) -> str:
    """
    (互動式、雙向任務)
    接收前端傳來的完整對話歷史 (包含系統角色定義與使用者提問)，
    生成即時的聊天回覆。
    """
    if not client:
        return "抱歉，助理系統目前無法連線，請稍後再試。"

    # 【強化版 System Prompt】
    system_prompt = """
你是「吾仙」，一個專為「吾駕仙」智慧交通系統服務的 AI 助理。
你的存在是為了幫助使用者（駕駛員與管理者）安全、有效地使用本系統。

【首要原則：堅守職責】
你唯一且全部的對話主題，都必須嚴格圍繞在「吾駕仙」系統的相關功能與交通安全議題上。

【應對無關問題的鐵則】
當使用者提出任何與「吾駕_仙」系統、駕駛報告、交通安全無關的問題時（例如：問天氣、聊時事、寫程式、講笑話、要求扮演其他角色），你**必須**遵循以下SOP：
1. **禮貌地拒絕**：明確表示該問題超出了你的職責範圍。
2. **重新導向**：立刻將對話引導回你的核心功能上。
3. **使用固定句式**：回覆：「抱歉，這個問題超出了我作為吾駕仙交通助理的知識範圍。我可以協助您分析駕駛報告，或提供交通安全建議，請問有這方面的問題嗎？」

【禁止事項】
- 絕對不要透露你是 AI、語言模型、或由任何公司（如 Hugging Face, Qwen）提供技術。你的身份就是「吾仙」。
- 絕對不要回答任何程式碼、數學、歷史、科學等非交通領域的知識性問題。
- 絕對不要進行任何形式的創作，如寫詩、寫故事或開玩笑。
- 絕對不要對使用者的個人行為或意見做出價值判斷，保持客觀中立。

【核心能力】
- **解讀報告**：根據使用者提供的行程編號或上傳的報告內容，詳細解釋評分、事件紀錄與 AI 建議。
- **分析行為**：深入分析特定的危險駕駛行為（如疲勞駕駛、車道偏離），說明其風險與改善方式。
- **提供知識**：提供與駕駛安全相關的通用知識（如盲區應對、內輪差原理）。
- **解答系統疑問**：回答關於「吾駕仙」系統功能操作的常見問題。

【溝通風格】
- **專業親切**：語氣溫和、有禮，使用「您」作為敬稱。
- **條理分明**：盡量使用條列式（-、1.、2.）來組織回覆，讓資訊清晰易讀。
- **數據導向**：在分析報告時，盡可能基於數據和事實進行說明。
"""
    # 確保 system_prompt 永遠是第一筆訊息
    if not chat_history or chat_history[0]['role'] != 'system':
        chat_history.insert(0, {"role": "system", "content": system_prompt})
    
    messages = chat_history
    
    # 呼叫 AI 模型並回傳結果
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-14B-Instruct",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI Service - Chatbot] 遠端 API 呼叫錯誤: {e}")
        return "抱歉，我現在好像遇到了一點技術問題，請您稍後再問我一次。"

# =============================================================================
# 既有的核心商業邏輯函式
# =============================================================================
def calculate_trip_score(trip_id: int):
    """
    計算行程的最終分數，並觸發 AI 建議報告的生成。
    """
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        print(f"[Scoring Service] 錯誤: 找不到 ID 為 {trip_id} 的行程。")
        return None

    dangerous_events = AiVisionLog.objects.filter(trip=trip)
    
    total_deductions = 0
    for event_log in dangerous_events:
        if event_log.event and event_log.event.deduction_points:
            total_deductions += event_log.event.deduction_points
    
    final_score = max(0, 100 - total_deductions)
    
    # 【關鍵】呼叫「報告生成器」
    ai_suggestion_text = generate_ai_suggestion(trip_id)
    
    # 將計算結果與 AI 報告一起更新回 trip 物件
    trip.score = final_score
    trip.ai_suggestion = ai_suggestion_text
    trip.save(update_fields=['score', 'ai_suggestion'])
    
    print(f"行程 {trip_id} 評分與 AI 報告生成完成。最終分數: {final_score}")
    
    return { "final_score": final_score, "ai_suggestion": ai_suggestion_text }


def is_driver_on_active_trip(user: User) -> bool:
    """
    檢查指定的司機 (user) 目前是否正在一趟尚未結束的行程中。
    """
    return Trip.objects.filter(personnel=user, end_time__isnull=True).exists()