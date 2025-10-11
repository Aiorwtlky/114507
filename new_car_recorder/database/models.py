# database/models.py (修正版)
"""
資料模型定義
定義本地資料庫的資料結構
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Trip:
    """行程資料模型"""
    trip_id: Optional[int] = None
    trip_number: Optional[str] = None
    user_id: Optional[int] = None
    nfc_uid: Optional[str] = None
    device_id: Optional[int] = None
    group_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    score: Optional[float] = None
    in_car_score: Optional[float] = None
    out_car_score: Optional[float] = None
    ai_suggestion: Optional[str] = None
    total_mileage: Optional[float] = None
    sync_status: str = 'pending'
    created_at: Optional[datetime] = None
    backend_trip_id: Optional[int] = None


@dataclass
class AIEvent:
    """AI 事件資料模型"""
    trip_id: int  # 必填欄位放前面
    event_code: str  # 必填欄位
    event_name: str  # 必填欄位
    timestamp: datetime  # 必填欄位
    camera_mode: str  # 必填欄位
    event_id: Optional[int] = None  # 有預設值的放後面
    confidence_score: Optional[float] = None
    event_details: Optional[str] = None
    deduction_points: int = 0
    interval_number: Optional[int] = None
    video_clip_path: Optional[str] = None
    video_clip_url: Optional[str] = None
    sync_status: str = 'pending'
    created_at: Optional[datetime] = None
    backend_event_id: Optional[int] = None


@dataclass
class VideoRecord:
    """影片記錄資料模型"""
    trip_id: int  # 必填欄位
    start_time: datetime  # 必填欄位
    local_path: str  # 必填欄位
    video_id: Optional[int] = None  # 有預設值的放後面
    video_number: Optional[str] = None
    end_time: Optional[datetime] = None
    video_url: Optional[str] = None
    file_size: Optional[int] = None
    camera_type: str = 'outer'
    sync_status: str = 'pending'
    upload_progress: float = 0.0
    created_at: Optional[datetime] = None
    backend_video_id: Optional[int] = None


@dataclass
class NFCMapping:
    """NFC UID 對應表（本地快取）"""
    nfc_uid: str  # 必填欄位
    user_id: int  # 必填欄位
    username: Optional[str] = None  # 有預設值的放後面
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    groups: Optional[List[dict]] = None
    last_updated: Optional[datetime] = None


@dataclass
class IntervalScore:
    """15 分鐘區間評分資料模型"""
    trip_id: int  # 必填欄位
    interval_number: int  # 必填欄位
    start_time: datetime  # 必填欄位
    end_time: datetime  # 必填欄位
    interval_id: Optional[int] = None  # 有預設值的放後面
    category_a_deductions: int = 0
    category_b_deductions: int = 0
    category_a_score: Optional[float] = None
    category_b_score: Optional[float] = None


# 事件代碼對照表
EVENT_SCORES = {
    # A 類 - 車內事件
    'A01': {'name': '重度疲勞 (閉眼超過5秒)', 'deduction': 40, 'category': 'A'},
    'A02': {'name': '中度疲勞 (閉眼超過3秒或PERCLOS過高)', 'deduction': 30, 'category': 'A'},
    'A03': {'name': '偵測到手持通話或操作手機', 'deduction': 15, 'category': 'A'},
    'A04': {'name': '臉部離開偵測區域', 'deduction': 40, 'category': 'A'},
    'A05': {'name': '視線長時間偏離', 'deduction': 5, 'category': 'A'},
    
    # B 類 - 車外事件
    'B01': {'name': '切換車道未打方向燈', 'deduction': 15, 'category': 'B'},
    'B02': {'name': '轉彎未打方向燈', 'deduction': 15, 'category': 'B'},
    'B03': {'name': '未保持適當車距', 'deduction': 15, 'category': 'B'},
    
    # 其他未列項目
    'A_OTHER': {'name': '其他車內事件', 'deduction': 5, 'category': 'A'},
    'B_OTHER': {'name': '其他車外事件', 'deduction': 5, 'category': 'B'},
}


def parse_event_code(event_string: str) -> tuple:
    """
    解析事件字串，提取事件代碼
    
    Args:
        event_string: 例如 "A01: 重度疲勞 (閉眼超過5秒)"
    
    Returns:
        (event_code, event_name)
    """
    if ':' in event_string:
        parts = event_string.split(':', 1)
        event_code = parts[0].strip()
        event_name = parts[1].strip()
        return event_code, event_name
    return event_string.strip(), event_string.strip()


def get_event_info(event_code: str) -> dict:
    """
    根據事件代碼取得事件資訊
    
    Args:
        event_code: 事件代碼（例如 'A01'）
    
    Returns:
        事件資訊字典
    """
    return EVENT_SCORES.get(event_code, {
        'name': '未知事件',
        'deduction': 5,
        'category': 'A' if event_code.startswith('A') else 'B'
    })