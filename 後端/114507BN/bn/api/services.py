# api/services.py

import os
import math
from datetime import timedelta
from dotenv import load_dotenv
from django.contrib.auth.models import User
from .models import Trip, AiVisionLog

# NEW: 匯入 Vertex AI 相關套件
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# =============================================================================
# 0. 初始化設定 (Initialization)
# =============================================================================
# 載入環境變數並初始化 Vertex AI client，確保整個模組共用以提升效率。
load_dotenv()

# NEW: Vertex AI 初始化區塊
gemini_model = None
try:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    if not project_id or not location:
        print("警告：未在 .env 檔案中找到 GOOGLE_CLOUD_PROJECT_ID 或 GOOGLE_CLOUD_LOCATION。")
    else:
        vertexai.init(project=project_id, location=location)
        # 我們選用 Flash 模型，它在速度和成本效益上表現優異，非常適合報告生成與聊天
        gemini_model = GenerativeModel("gemini-1.5-flash-001")
        print("✅ Vertex AI Gemini 連線成功。")
except Exception as e:
    print(f"❌ Vertex AI 初始化失敗: {e}")
    print("警告：AI 相關功能將無法運作。")


# =============================================================================
# 1. 核心商業邏輯 (Core Business Logic)
# (這整個區塊完全不需要修改，因為它與 AI 模型的呼叫無關)
# =============================================================================

def calculate_trip_score(trip_id: int):
    """
    【全新計分邏輯】
    根據時間區間 (15分鐘) 和事件分類 (車內/車外)，計算行程的最終分數，
    並觸發 AI 建議報告的生成。
    
    Args:
        trip_id (int): 要計算分數的行程 ID。
        
    Returns:
        dict: 包含最終分數的字典，或在錯誤時回傳 None。
    """
    try:
        trip = Trip.objects.get(id=trip_id)
        if not trip.start_time or not trip.end_time:
            print(f"[Scoring Service] 錯誤: 行程 {trip_id} 缺少開始或結束時間，無法計分。")
            return None
    except Trip.DoesNotExist:
        print(f"[Scoring Service] 錯誤: 找不到 ID 為 {trip_id} 的行程。")
        return None

    events = AiVisionLog.objects.filter(trip=trip).select_related('event')
    
    # 狀況一：如果沒有任何違規事件，直接給滿分。
    if not events.exists():
        trip.in_car_score = 100
        trip.out_car_score = 100
        trip.score = 100
        trip.ai_suggestion = "本次行程表現良好，未偵測到任何危險駕駛行為。請繼續保持！"
        trip.save(update_fields=['in_car_score', 'out_car_score', 'score', 'ai_suggestion'])
        print(f"行程 {trip_id} 無違規事件，評為滿分。")
        return { "final_score": 100, "in_car_score": 100, "out_car_score": 100 }

    # 狀況二：有違規事件，開始複雜計分。
    # 步驟 1: 將行程切分為 15 分鐘的時間區間。
    intervals = []
    current_time = trip.start_time
    while current_time < trip.end_time:
        interval_end = current_time + timedelta(minutes=15)
        intervals.append({'start': current_time, 'end': interval_end, 'in_car_deductions': 0, 'out_car_deductions': 0})
        current_time = interval_end

    # 步驟 2: 將所有事件分配到對應的時間區間與類別。
    for event in events:
        for interval in intervals:
            if interval['start'] <= event.timestamp < interval['end']:
                # 根據 event_number 前綴判斷類別 ('A'為車內, 'B'為車外)
                category = event.event.event_number[0].upper()
                deduction = event.event.deduction_points or 0
                
                if category == 'A':
                    interval['in_car_deductions'] += deduction
                elif category == 'B':
                    interval['out_car_deductions'] += deduction
                break

    # 步驟 3: 計算每個區間的車內/車外分數 (最低為0分)。
    in_car_interval_scores = [max(0, 100 - i['in_car_deductions']) for i in intervals if i['in_car_deductions'] > 0]
    out_car_interval_scores = [max(0, 100 - i['out_car_deductions']) for i in intervals if i['out_car_deductions'] > 0]
    
    # 輔助函式，用於執行 "有低於60取最低，否則取平均" 的規則
    def _get_final_category_score(scores: list):
        if not scores: # 如果該類別完全沒有違規，就是滿分
            return 100.0
        if any(s < 60 for s in scores):
            return float(min(scores))
        else:
            return sum(scores) / len(scores)

    # 步驟 4: 根據規則計算最終的車內/車外總分。
    final_in_car_score = _get_final_category_score(in_car_interval_scores)
    final_out_car_score = _get_final_category_score(out_car_interval_scores)

    # 步驟 5: 計算最終總分。
    final_score = (final_in_car_score + final_out_car_score) / 2

    # 步驟 6: 呼叫 AI 建議生成器。
    ai_suggestion_text = generate_ai_suggestion(trip_id)
    
    # 步驟 7: 將所有分數與 AI 報告一起更新回資料庫。
    trip.in_car_score = final_in_car_score
    trip.out_car_score = final_out_car_score
    trip.score = final_score
    trip.ai_suggestion = ai_suggestion_text
    trip.save(update_fields=['in_car_score', 'out_car_score', 'score', 'ai_suggestion'])
    
    print(f"行程 {trip_id} 新版評分完成。車內: {final_in_car_score:.1f}, 車外: {final_out_car_score:.1f}, 總分: {final_score:.1f}")
    
    return { 
        "final_score": final_score, 
        "in_car_score": final_in_car_score, 
        "out_car_score": final_out_car_score,
        "ai_suggestion": ai_suggestion_text 
    }

def is_driver_on_active_trip(user: User) -> bool:
    """
    檢查指定的司機 (user) 目前是否正在一趟尚未結束的行程中。
    
    Args:
        user (User): Django 的使用者物件。
        
    Returns:
        bool: 如果使用者有進行中的行程則回傳 True，否則回傳 False。
    """
    return Trip.objects.filter(personnel=user, end_time__isnull=True).exists()


# =============================================================================
# 2. AI 服務 (AI Services)
# =============================================================================

# 2.1. 行程總結報告產生器
def generate_ai_suggestion(trip_id: int) -> str:
    """
    (自動化、單向任務)
    根據單趟行程的所有危險事件，生成一份正式、客觀的駕駛行為改善建議報告。
    """
    # MODIFIED: 檢查 Gemini 模型是否初始化成功
    if not gemini_model:
        return "系統設定錯誤：Vertex AI 初始化失敗。"

    try:
        events = AiVisionLog.objects.filter(trip_id=trip_id)
        if not events.exists():
            return "本次行程表現良好，未偵測到明顯的危險駕駛行為。請繼續保持安全駕駛。"
    except Exception:
        return "系統錯誤：查詢行程事件時發生錯誤。"

    event_summary = "\n".join([f"- 事件：{log.event.description}，細節：{log.event_details}" for log in events])
    system_prompt = "你是一位專業的智慧駕駛安全分析師「吾仙」。任務是根據一份危險駕駛事件清單，撰寫一份客觀、專業、且具建設性的駕駛行為改善建議報告。請避免口語化，並以條列式呈現重點。"
    user_prompt = f"請分析以下行程的危險駕駛事件，並生成改善建議報告：\n\n【危險事件清單】\n{event_summary}\n\n請條列主要的風險點，並提供具體改善建議。"
    
    # MODIFIED: Gemini 的 messages 格式與您原本的完全相容
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    try:
        # MODIFIED: 建立 Gemini 的生成設定
        generation_config = GenerationConfig(
            temperature=0.5,
            max_output_tokens=300
        )
        # MODIFIED: 呼叫 Gemini 模型
        response = gemini_model.generate_content(
            messages,
            generation_config=generation_config
        )
        # MODIFIED: Gemini 回應的格式更簡潔
        return response.text.strip()
    except Exception as e:
        print(f"[AI Service - Suggestion] Vertex AI API 呼叫錯誤: {e}")
        return f"系統分析您本次行程有以下事件：\n{event_summary}\n\n建議您注意改善駕駛習慣，確保行車安全。"

# 2.2. 即時對話回應器
def get_chatbot_response(chat_history: list) -> str:
    """
    (互動式、雙向任務)
    接收前端傳來的完整對話歷史，生成即時的聊天回覆。
    """
    # MODIFIED: 檢查 Gemini 模型是否初始化成功
    if not gemini_model:
        return "抱歉，助理系統目前無法連線，請稍後再試。"

    system_prompt = """
你是「吾仙」，一個專為「吾駕仙」智慧交通系統服務的 AI 助理。
你的唯一職責是圍繞「吾駕仙」系統功能與交通安全議題進行對話。
當使用者提出任何無關問題時（如天氣、新聞、寫程式），你**必須**使用固定句式回答：「抱歉，這個問題超出了我作為吾駕仙交通助理的知識範圍。我可以協助您分析駕駛報告，或提供交通安全建議，請問有這方面的問題嗎？」
【禁止事項】
- 絕對不要透露你是 AI 或語言模型。
- 絕對不要回答任何非交通領域的知識性問題。
【核心能力】
- 解讀駕駛報告、分析危險駕駛行為、提供交通安全知識、解答系統操作疑問。
【溝通風格】
- 專業親切，條理分明。
"""
    if not chat_history or chat_history[0]['role'] != 'system':
        chat_history.insert(0, {"role": "system", "content": system_prompt})
    
    try:
        # MODIFIED: 建立 Gemini 的生成設定
        generation_config = GenerationConfig(
            temperature=0.7,
            max_output_tokens=512
        )
        # MODIFIED: 呼叫 Gemini 模型
        # 對於多輪對話，可以直接傳入整個 history list
        response = gemini_model.generate_content(
            chat_history,
            generation_config=generation_config
        )
        # MODIFIED: Gemini 回應的格式更簡潔
        return response.text.strip()
    except Exception as e:
        print(f"[AI Service - Chatbot] Vertex AI API 呼叫錯誤: {e}")
        return "抱歉，我現在好像遇到了一點技術問題，請您稍後再問我一次。"