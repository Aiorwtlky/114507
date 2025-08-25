# 智慧駕駛安全管理系統 - AI模型整合
# Smart Driving Safety Management System - AI Models Integration
# 版本: 1.0
# 作者: AI Assistant
# 日期: 2025-08-25

import tensorflow as tf
import cv2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Tuple, Optional
import sqlite3
from dataclasses import dataclass
from threading import Thread
import time

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """偵測結果資料結構"""
    timestamp: datetime
    detection_type: str
    confidence: float
    severity: str
    description: str
    is_violation: bool

@dataclass
class RiskAssessment:
    """風險評估結果"""
    overall_risk: float
    fatigue_risk: float
    attention_risk: float
    behavior_risk: float
    recommendations: List[str]

class FatigueDetectionModel:
    """疲勞駕駛偵測模型"""
    
    def __init__(self):
        self.model = self._build_model()
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def _build_model(self):
        """建立疲勞偵測CNN模型"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')  # 清醒/疲勞/極度疲勞
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model
    
    def detect_eyes(self, frame):
        """偵測眼部區域"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 4)
            
            if len(eyes) >= 2:
                # 提取眼部區域進行疲勞分析
                eye_region = frame[y:y+h, x:x+w]
                return cv2.resize(eye_region, (64, 64))
        
        return None
    
    def predict_fatigue(self, frame) -> DetectionResult:
        """預測疲勞程度"""
        eye_region = self.detect_eyes(frame)
        
        if eye_region is None:
            return DetectionResult(
                timestamp=datetime.now(),
                detection_type='fatigue',
                confidence=0.0,
                severity='normal',
                description='無法偵測到眼部',
                is_violation=False
            )
        
        # 預處理
        eye_region = np.expand_dims(eye_region.astype('float32') / 255.0, axis=0)
        
        # 模型預測
        prediction = self.model.predict(eye_region, verbose=0)[0]
        fatigue_level = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        # 判斷結果
        if fatigue_level == 0:  # 清醒
            severity = 'normal'
            description = '駕駛員狀態正常'
            is_violation = False
        elif fatigue_level == 1:  # 疲勞
            severity = 'warning'
            description = '偵測到輕微疲勞，建議注意休息'
            is_violation = True
        else:  # 極度疲勞
            severity = 'danger'
            description = '偵測到嚴重疲勞，請立即停車休息'
            is_violation = True
        
        return DetectionResult(
            timestamp=datetime.now(),
            detection_type='fatigue',
            confidence=confidence,
            severity=severity,
            description=description,
            is_violation=is_violation
        )

class AttentionTrackingModel:
    """注意力追蹤模型"""
    
    def __init__(self):
        self.model = self._build_model()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def _build_model(self):
        """建立注意力追蹤模型"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(4, activation='softmax')  # 前方/左/右/下(手機)
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model
    
    def detect_head_pose(self, frame) -> DetectionResult:
        """偵測頭部姿勢和注意力方向"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return DetectionResult(
                timestamp=datetime.now(),
                detection_type='distraction',
                confidence=0.0,
                severity='normal',
                description='無法偵測到面部',
                is_violation=False
            )
        
        # 取最大的臉部區域
        (x, y, w, h) = max(faces, key=lambda face: face[2] * face[3])
        face_region = frame[y:y+h, x:x+w]
        face_region = cv2.resize(face_region, (128, 128))
        face_region = np.expand_dims(face_region.astype('float32') / 255.0, axis=0)
        
        # 預測注意力方向
        prediction = self.model.predict(face_region, verbose=0)[0]
        direction = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        directions = ['forward', 'left', 'right', 'down']
        direction_name = directions[direction]
        
        # 判斷是否分心
        if direction == 0:  # 前方
            severity = 'normal'
            description = '注意力集中在前方'
            is_violation = False
        elif direction in [1, 2]:  # 左右
            if confidence > 0.8:
                severity = 'warning'
                description = f'注意力偏向{direction_name}，請專心駕駛'
                is_violation = True
            else:
                severity = 'normal'
                description = '輕微轉頭，屬正常範圍'
                is_violation = False
        else:  # 向下 (可能看手機)
            severity = 'danger'
            description = '疑似使用手機，請立即停止'
            is_violation = True
        
        return DetectionResult(
            timestamp=datetime.now(),
            detection_type='distraction',
            confidence=confidence,
            severity=severity,
            description=description,
            is_violation=is_violation
        )

class BehaviorDetectionModel:
    """駕駛行為偵測模型"""
    
    def __init__(self):
        self.phone_model = self._build_phone_detection_model()
        self.seatbelt_model = self._build_seatbelt_detection_model()
        
    def _build_phone_detection_model(self):
        """手機使用偵測模型"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(2, activation='softmax')  # 使用/未使用手機
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model
    
    def _build_seatbelt_detection_model(self):
        """安全帶偵測模型"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(2, activation='softmax')  # 有/無安全帶
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return model
    
    def detect_phone_usage(self, frame) -> DetectionResult:
        """偵測手機使用"""
        resized_frame = cv2.resize(frame, (224, 224))
        processed_frame = np.expand_dims(resized_frame.astype('float32') / 255.0, axis=0)
        
        prediction = self.phone_model.predict(processed_frame, verbose=0)[0]
        using_phone = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        if using_phone == 1 and confidence > 0.7:
            return DetectionResult(
                timestamp=datetime.now(),
                detection_type='phone_usage',
                confidence=confidence,
                severity='danger',
                description='偵測到使用手機，請立即停止',
                is_violation=True
            )
        
        return DetectionResult(
            timestamp=datetime.now(),
            detection_type='phone_usage',
            confidence=confidence,
            severity='normal',
            description='未偵測到手機使用',
            is_violation=False
        )
    
    def detect_seatbelt(self, frame) -> DetectionResult:
        """偵測安全帶配戴"""
        resized_frame = cv2.resize(frame, (224, 224))
        processed_frame = np.expand_dims(resized_frame.astype('float32') / 255.0, axis=0)
        
        prediction = self.seatbelt_model.predict(processed_frame, verbose=0)[0]
        wearing_seatbelt = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        if wearing_seatbelt == 0 and confidence > 0.8:
            return DetectionResult(
                timestamp=datetime.now(),
                detection_type='no_seatbelt',
                confidence=confidence,
                severity='warning',
                description='未繫安全帶，請立即繫上',
                is_violation=True
            )
        
        return DetectionResult(
            timestamp=datetime.now(),
            detection_type='seatbelt',
            confidence=confidence,
            severity='normal',
            description='已正確繫上安全帶',
            is_violation=False
        )

class RiskAssessmentModel:
    """風險評估模型"""
    
    def __init__(self):
        self.lstm_model = self._build_lstm_model()
        self.risk_threshold = 0.7
        
    def _build_lstm_model(self):
        """建立LSTM風險預測模型"""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(10, 8)),  # 10個時間步，8個特徵
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(1, activation='sigmoid')  # 風險機率
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        return model
    
    def calculate_risk(self, detection_history: List[DetectionResult]) -> RiskAssessment:
        """計算綜合風險評估"""
        if len(detection_history) < 10:
            return RiskAssessment(
                overall_risk=0.1,
                fatigue_risk=0.1,
                attention_risk=0.1,
                behavior_risk=0.1,
                recommendations=['需要更多駕駛數據進行準確評估']
            )
        
        # 準備時間序列數據
        features = []
        for detection in detection_history[-10:]:  # 最近10筆記錄
            feature_vector = [
                1.0 if detection.detection_type == 'fatigue' else 0.0,
                1.0 if detection.detection_type == 'distraction' else 0.0,
                1.0 if detection.detection_type == 'phone_usage' else 0.0,
                1.0 if detection.detection_type == 'no_seatbelt' else 0.0,
                detection.confidence,
                1.0 if detection.severity == 'warning' else 0.0,
                1.0 if detection.severity == 'danger' else 0.0,
                1.0 if detection.is_violation else 0.0
            ]
            features.append(feature_vector)
        
        # 預測風險
        input_data = np.array([features])  # 形狀: (1, 10, 8)
        overall_risk = float(self.lstm_model.predict(input_data, verbose=0)[0][0])
        
        # 計算各項風險
        fatigue_detections = [d for d in detection_history[-20:] if d.detection_type == 'fatigue' and d.is_violation]
        attention_detections = [d for d in detection_history[-20:] if d.detection_type == 'distraction' and d.is_violation]
        behavior_detections = [d for d in detection_history[-20:] if d.detection_type in ['phone_usage', 'no_seatbelt'] and d.is_violation]
        
        fatigue_risk = min(len(fatigue_detections) / 5.0, 1.0)
        attention_risk = min(len(attention_detections) / 10.0, 1.0)
        behavior_risk = min(len(behavior_detections) / 3.0, 1.0)
        
        # 生成建議
        recommendations = self._generate_recommendations(overall_risk, fatigue_risk, attention_risk, behavior_risk)
        
        return RiskAssessment(
            overall_risk=overall_risk,
            fatigue_risk=fatigue_risk,
            attention_risk=attention_risk,
            behavior_risk=behavior_risk,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, overall_risk: float, fatigue_risk: float, 
                                attention_risk: float, behavior_risk: float) -> List[str]:
        """生成個人化建議"""
        recommendations = []
        
        if overall_risk > 0.8:
            recommendations.append("🚨 整體風險過高，建議立即停車休息")
        elif overall_risk > 0.6:
            recommendations.append("⚠️ 風險偏高，請提高警覺")
        
        if fatigue_risk > 0.7:
            recommendations.append("😴 疲勞程度嚴重，建議睡眠至少6小時後再駕駛")
        elif fatigue_risk > 0.4:
            recommendations.append("💤 出現疲勞跡象，建議休息15-30分鐘")
        
        if attention_risk > 0.6:
            recommendations.append("👀 注意力不集中，請專心注視前方道路")
        elif attention_risk > 0.3:
            recommendations.append("🎯 保持專注，避免分心")
        
        if behavior_risk > 0.5:
            recommendations.append("📱 請遵守駕駛安全規範，勿使用手機")
        
        if overall_risk < 0.3:
            recommendations.append("✅ 駕駛狀態良好，請繼續保持")
        
        return recommendations

class PersonalizedRecommendationSystem:
    """個人化建議系統"""
    
    def __init__(self):
        self.db_path = 'driver_history.db'
        self._init_database()
    
    def _init_database(self):
        """初始化資料庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id TEXT,
                timestamp TEXT,
                detection_type TEXT,
                confidence REAL,
                severity TEXT,
                is_violation INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_detection(self, driver_id: str, detection: DetectionResult):
        """儲存偵測結果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detection_history 
            (driver_id, timestamp, detection_type, confidence, severity, is_violation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            driver_id,
            detection.timestamp.isoformat(),
            detection.detection_type,
            detection.confidence,
            detection.severity,
            1 if detection.is_violation else 0
        ))
        conn.commit()
        conn.close()
    
    def get_driver_history(self, driver_id: str, days: int = 30) -> List[DetectionResult]:
        """取得駕駛員歷史記錄"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT timestamp, detection_type, confidence, severity, is_violation
            FROM detection_history
            WHERE driver_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (driver_id, since_date))
        
        results = []
        for row in cursor.fetchall():
            results.append(DetectionResult(
                timestamp=datetime.fromisoformat(row[0]),
                detection_type=row[1],
                confidence=row[2],
                severity=row[3],
                description="",
                is_violation=bool(row[4])
            ))
        
        conn.close()
        return results
    
    def generate_personal_report(self, driver_id: str) -> Dict:
        """生成個人化駕駛報告"""
        history = self.get_driver_history(driver_id, days=30)
        
        if not history:
            return {
                'driver_id': driver_id,
                'period': '過去30天',
                'total_detections': 0,
                'violation_rate': 0.0,
                'risk_trends': [],
                'recommendations': ['需要更多駕駛數據']
            }
        
        # 統計分析
        total_detections = len(history)
        violations = [h for h in history if h.is_violation]
        violation_rate = len(violations) / total_detections if total_detections > 0 else 0
        
        # 違規類型分析
        violation_types = {}
        for v in violations:
            violation_types[v.detection_type] = violation_types.get(v.detection_type, 0) + 1
        
        # 時間趨勢分析
        risk_trends = self._calculate_risk_trends(history)
        
        # 個人化建議
        recommendations = self._generate_personalized_recommendations(
            violation_rate, violation_types, risk_trends
        )
        
        return {
            'driver_id': driver_id,
            'period': '過去30天',
            'total_detections': total_detections,
            'violation_count': len(violations),
            'violation_rate': round(violation_rate * 100, 2),
            'violation_types': violation_types,
            'risk_trends': risk_trends,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_risk_trends(self, history: List[DetectionResult]) -> List[Dict]:
        """計算風險趨勢"""
        # 按週統計風險
        trends = []
        for week in range(4):  # 最近4週
            start_date = datetime.now() - timedelta(weeks=week+1)
            end_date = datetime.now() - timedelta(weeks=week)
            
            week_detections = [
                h for h in history 
                if start_date <= h.timestamp <= end_date
            ]
            week_violations = [h for h in week_detections if h.is_violation]
            
            trends.append({
                'week': f'第{4-week}週',
                'total_detections': len(week_detections),
                'violations': len(week_violations),
                'risk_score': len(week_violations) / max(len(week_detections), 1) * 100
            })
        
        return trends
    
    def _generate_personalized_recommendations(self, violation_rate: float, 
                                             violation_types: Dict, 
                                             risk_trends: List[Dict]) -> List[str]:
        """生成個人化建議"""
        recommendations = []
        
        # 根據違規率給建議
        if violation_rate > 0.3:
            recommendations.append("🚨 違規率過高，需要加強安全駕駛意識")
        elif violation_rate > 0.1:
            recommendations.append("⚠️ 有改善空間，建議多注意駕駛習慣")
        else:
            recommendations.append("✅ 駕駛表現良好，請繼續保持")
        
        # 根據主要違規類型給建議
        if 'fatigue' in violation_types:
            count = violation_types['fatigue']
            if count > 5:
                recommendations.append("😴 疲勞駕駛頻繁，建議調整作息，確保充足睡眠")
            else:
                recommendations.append("💤 注意休息，避免疲勞駕駛")
        
        if 'distraction' in violation_types:
            count = violation_types['distraction']
            if count > 10:
                recommendations.append("👀 經常分心，建議專心駕駛訓練")
            else:
                recommendations.append("🎯 保持專注，注視前方道路")
        
        if 'phone_usage' in violation_types:
            recommendations.append("📱 請使用免持裝置，避免手持手機")
        
        if 'no_seatbelt' in violation_types:
            recommendations.append("🔒 養成上車即繫安全帶的習慣")
        
        # 根據趨勢給建議
        if len(risk_trends) >= 2:
            recent_risk = risk_trends[0]['risk_score']
            previous_risk = risk_trends[1]['risk_score']
            
            if recent_risk > previous_risk:
                recommendations.append("📈 風險有上升趨勢，請提高警覺")
            elif recent_risk < previous_risk:
                recommendations.append("📉 風險下降中，表現進步！")
        
        return recommendations

class SmartDrivingSafetySystem:
    """智慧駕駛安全管理系統主類"""
    
    def __init__(self):
        # 初始化所有AI模型
        logger.info("正在初始化AI模型...")
        self.fatigue_detector = FatigueDetectionModel()
        self.attention_tracker = AttentionTrackingModel()
        self.behavior_detector = BehaviorDetectionModel()
        self.risk_assessor = RiskAssessmentModel()
        self.recommendation_system = PersonalizedRecommendationSystem()
        
        # 系統狀態
        self.is_monitoring = False
        self.current_driver_id = None
        self.detection_buffer = []
        
        logger.info("✅ 智慧駕駛安全管理系統初始化完成")
    
    def start_monitoring(self, driver_id: str, video_source: int = 0):
        """開始監控駕駛"""
        logger.info(f"開始監控駕駛員: {driver_id}")
        
        self.current_driver_id = driver_id
        self.is_monitoring = True
        self.detection_buffer = []
        
        # 啟動攝影機
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            logger.error("無法開啟攝影機")
            return
        
        try:
            while self.is_monitoring:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("無法讀取影像")
                    continue
                
                # 執行所有AI偵測
                results = self._process_frame(frame)
                
                # 儲存結果
                for result in results:
                    if result.confidence > 0.5:  # 只儲存信心度高的結果
                        self.detection_buffer.append(result)
                        self.recommendation_system.save_detection(driver_id, result)
                
                # 即時風險評估
                if len(self.detection_buffer) >= 10:
                    risk_assessment = self.risk_assessor.calculate_risk(self.detection_buffer[-20:])
                    
                    # 高風險警告
                    if risk_assessment.overall_risk > 0.8:
                        self._trigger_emergency_alert(risk_assessment)
                    elif risk_assessment.overall_risk > 0.6:
                        self._trigger_warning_alert(risk_assessment)
                
                # 顯示即時偵測結果
                annotated_frame = self._annotate_frame(frame, results)
                cv2.imshow('Smart Driving Safety Monitor', annotated_frame)
                
                # 按 'q' 退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # 控制幀率
                time.sleep(0.033)  # 約30 FPS
                
        except KeyboardInterrupt:
            logger.info("監控被用戶中斷")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.is_monitoring = False
            logger.info("監控已停止")
    
    def _process_frame(self, frame) -> List[DetectionResult]:
        """處理單幀影像，執行所有AI偵測"""
        results = []
        
        try:
            # 疲勞偵測
            fatigue_result = self.fatigue_detector.predict_fatigue(frame)
            results.append(fatigue_result)
            
            # 注意力追蹤
            attention_result = self.attention_tracker.detect_head_pose(frame)
            results.append(attention_result)
            
            # 手機使用偵測
            phone_result = self.behavior_detector.detect_phone_usage(frame)
            results.append(phone_result)
            
            # 安全帶偵測
            seatbelt_result = self.behavior_detector.detect_seatbelt(frame)
            results.append(seatbelt_result)
            
        except Exception as e:
            logger.error(f"處理幀時發生錯誤: {e}")
        
        return results
    
    def _annotate_frame(self, frame, results: List[DetectionResult]):
        """在影像上標註偵測結果"""
        annotated = frame.copy()
        height, width = frame.shape[:2]
        
        # 設定顏色
        colors = {
            'normal': (0, 255, 0),    # 綠色
            'warning': (0, 165, 255), # 橘色
            'danger': (0, 0, 255)     # 紅色
        }
        
        # 繪製偵測結果
        y_offset = 30
        for result in results:
            if result.confidence > 0.3:  # 只顯示有意義的結果
                color = colors.get(result.severity, (255, 255, 255))
                
                # 顯示文字
                text = f"{result.detection_type}: {result.confidence:.2f}"
                cv2.putText(annotated, text, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # 違規警告
                if result.is_violation:
                    cv2.putText(annotated, "WARNING!", 
                               (width - 150, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                y_offset += 25
        
        # 顯示時間戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated, timestamp, (10, height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated
    
    def _trigger_emergency_alert(self, risk_assessment: RiskAssessment):
        """觸發緊急警告"""
        alert_message = f"""
🚨 緊急警告 🚨
駕駛員: {self.current_driver_id}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
風險等級: 極高 ({risk_assessment.overall_risk:.2%})

風險分析:
- 疲勞風險: {risk_assessment.fatigue_risk:.2%}
- 注意力風險: {risk_assessment.attention_risk:.2%}  
- 行為風險: {risk_assessment.behavior_risk:.2%}

建議立即停車休息！
        """
        logger.warning(alert_message)
        print(alert_message)
    
    def _trigger_warning_alert(self, risk_assessment: RiskAssessment):
        """觸發一般警告"""
        alert_message = f"""
⚠️  駕駛警告 ⚠️
風險等級: 偏高 ({risk_assessment.overall_risk:.2%})
建議: {', '.join(risk_assessment.recommendations[:2])}
        """
        logger.info(alert_message)
        print(alert_message)
    
    def stop_monitoring(self):
        """停止監控"""
        self.is_monitoring = False
        logger.info("正在停止監控...")
    
    def generate_driver_report(self, driver_id: str) -> Dict:
        """生成駕駛員完整報告"""
        logger.info(f"正在生成駕駛員 {driver_id} 的報告...")
        
        # 基本統計報告
        basic_report = self.recommendation_system.generate_personal_report(driver_id)
        
        # 風險評估
        history = self.recommendation_system.get_driver_history(driver_id, days=30)
        if len(history) >= 10:
            risk_assessment = self.risk_assessor.calculate_risk(history[-20:])
        else:
            risk_assessment = RiskAssessment(0.1, 0.1, 0.1, 0.1, ['數據不足'])
        
        # 整合完整報告
        comprehensive_report = {
            **basic_report,
            'current_risk_assessment': {
                'overall_risk': risk_assessment.overall_risk,
                'fatigue_risk': risk_assessment.fatigue_risk,
                'attention_risk': risk_assessment.attention_risk,
                'behavior_risk': risk_assessment.behavior_risk,
                'ai_recommendations': risk_assessment.recommendations
            },
            'safety_score': self._calculate_safety_score(basic_report, risk_assessment),
            'improvement_suggestions': self._generate_improvement_plan(basic_report, risk_assessment)
        }
        
        return comprehensive_report
    
    def _calculate_safety_score(self, basic_report: Dict, risk_assessment: RiskAssessment) -> Dict:
        """計算安全評分"""
        violation_rate = basic_report.get('violation_rate', 0) / 100
        overall_risk = risk_assessment.overall_risk
        
        # 綜合評分 (0-100)
        base_score = 100
        penalty = (violation_rate * 40) + (overall_risk * 30)
        final_score = max(0, base_score - penalty)
        
        # 等級評定
        if final_score >= 90:
            grade = 'A+'
            description = '優秀駕駛'
        elif final_score >= 80:
            grade = 'A'
            description = '良好駕駛'
        elif final_score >= 70:
            grade = 'B'
            description = '普通駕駛'
        elif final_score >= 60:
            grade = 'C'
            description = '需要改善'
        else:
            grade = 'D'
            description = '高風險駕駛'
        
        return {
            'score': round(final_score, 1),
            'grade': grade,
            'description': description,
            'max_score': 100
        }
    
    def _generate_improvement_plan(self, basic_report: Dict, risk_assessment: RiskAssessment) -> List[Dict]:
        """生成改善計劃"""
        plans = []
        
        violation_types = basic_report.get('violation_types', {})
        
        # 疲勞駕駛改善
        if 'fatigue' in violation_types and violation_types['fatigue'] > 3:
            plans.append({
                'category': '疲勞管理',
                'priority': 'high',
                'actions': [
                    '確保每日睡眠時間至少7-8小時',
                    '長途駕駛每2小時休息15分鐘',
                    '避免在疲勞高峰時段（下午2-4點）駕駛',
                    '考慮使用疲勞監測應用程式'
                ],
                'target': '將疲勞違規減少50%'
            })
        
        # 注意力改善
        if 'distraction' in violation_types and violation_types['distraction'] > 5:
            plans.append({
                'category': '專注力訓練',
                'priority': 'medium',
                'actions': [
                    '練習正念駕駛技巧',
                    '設定免干擾駕駛模式',
                    '使用語音助手替代手動操作',
                    '定期進行專注力訓練'
                ],
                'target': '提高專注度，減少分心事件'
            })
        
        # 行為規範改善
        if any(key in violation_types for key in ['phone_usage', 'no_seatbelt']):
            plans.append({
                'category': '安全習慣',
                'priority': 'high',
                'actions': [
                    '使用車載藍牙系統',
                    '將手機放在不易取得的位置',
                    '養成上車立即繫安全帶的習慣',
                    '定期參加安全駕駛課程'
                ],
                'target': '建立良好的安全駕駛習慣'
            })
        
        # 總體風險管理
        if risk_assessment.overall_risk > 0.5:
            plans.append({
                'category': '綜合風險管理',
                'priority': 'high',
                'actions': [
                    '制定個人駕駛安全檢查清單',
                    '定期檢視駕駛表現數據',
                    '尋求專業駕駛教練指導',
                    '考慮參加防禦性駕駛課程'
                ],
                'target': '將整體風險降低至安全水準'
            })
        
        return plans
    
    def export_report_to_file(self, driver_id: str, file_format: str = 'json') -> str:
        """匯出報告到檔案"""
        report = self.generate_driver_report(driver_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if file_format.lower() == 'json':
            filename = f"driver_report_{driver_id}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        elif file_format.lower() == 'txt':
            filename = f"driver_report_{driver_id}_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self._format_report_as_text(report))
        
        logger.info(f"報告已匯出至: {filename}")
        return filename
    
    def _format_report_as_text(self, report: Dict) -> str:
        """將報告格式化為文字"""
        text_report = f"""
智慧駕駛安全分析報告
==================

駕駛員ID: {report['driver_id']}
報告期間: {report['period']}
生成時間: {report['generated_at']}

基本統計
--------
總偵測次數: {report['total_detections']}
違規次數: {report['violation_count']}
違規率: {report['violation_rate']}%

安全評分
--------
綜合評分: {report['safety_score']['score']}/100
安全等級: {report['safety_score']['grade']}
評價: {report['safety_score']['description']}

風險評估
--------
整體風險: {report['current_risk_assessment']['overall_risk']:.2%}
疲勞風險: {report['current_risk_assessment']['fatigue_risk']:.2%}
注意力風險: {report['current_risk_assessment']['attention_risk']:.2%}
行為風險: {report['current_risk_assessment']['behavior_risk']:.2%}

AI建議
------
"""
        
        for i, rec in enumerate(report['current_risk_assessment']['ai_recommendations'], 1):
            text_report += f"{i}. {rec}\n"
        
        text_report += "\n改善計劃\n--------\n"
        
        for plan in report['improvement_suggestions']:
            text_report += f"\n{plan['category']} (優先級: {plan['priority']})\n"
            text_report += f"目標: {plan['target']}\n"
            text_report += "行動方案:\n"
            for action in plan['actions']:
                text_report += f"  • {action}\n"
        
        return text_report

def demo_system():
    """系統演示功能"""
    print("🚗 智慧駕駛安全管理系統演示")
    print("=" * 50)
    
    # 初始化系統
    system = SmartDrivingSafetySystem()
    
    # 模擬駕駛員數據
    demo_driver_id = "DEMO_001"
    
    print(f"\n正在為駕駛員 {demo_driver_id} 生成演示數據...")
    
    # 模擬一些偵測記錄
    demo_detections = [
        DetectionResult(datetime.now() - timedelta(minutes=30), 'fatigue', 0.8, 'warning', '輕微疲勞', True),
        DetectionResult(datetime.now() - timedelta(minutes=25), 'distraction', 0.6, 'warning', '注意力分散', True),
        DetectionResult(datetime.now() - timedelta(minutes=20), 'phone_usage', 0.9, 'danger', '使用手機', True),
        DetectionResult(datetime.now() - timedelta(minutes=15), 'fatigue', 0.3, 'normal', '狀態正常', False),
        DetectionResult(datetime.now() - timedelta(minutes=10), 'seatbelt', 0.95, 'normal', '已繫安全帶', False),
        DetectionResult(datetime.now() - timedelta(minutes=5), 'distraction', 0.75, 'warning', '輕微分心', True),
    ]
    
    # 儲存演示數據
    for detection in demo_detections:
        system.recommendation_system.save_detection(demo_driver_id, detection)
    
    print("✅ 演示數據已生成")
    
    # 生成報告
    print("\n正在生成駕駛報告...")
    report = system.generate_driver_report(demo_driver_id)
    
    # 顯示報告摘要
    print("\n📊 駕駛報告摘要:")
    print(f"安全評分: {report['safety_score']['score']}/100 ({report['safety_score']['grade']})")
    print(f"違規率: {report['violation_rate']}%")
    print(f"整體風險: {report['current_risk_assessment']['overall_risk']:.2%}")
    
    print("\n💡 AI建議:")
    for i, rec in enumerate(report['current_risk_assessment']['ai_recommendations'][:3], 1):
        print(f"  {i}. {rec}")
    
    # 匯出報告
    filename = system.export_report_to_file(demo_driver_id, 'json')
    print(f"\n💾 完整報告已匯出至: {filename}")
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("您可以使用以下指令開始即時監控:")
    print("system.start_monitoring('YOUR_DRIVER_ID')")

if __name__ == "__main__":
    # 運行演示
    demo_system()
    
    # 如需即時監控，請取消下面的註解
    # system = SmartDrivingSafetySystem()
    # system.start_monitoring('DRIVER_001')  # 開始監控攝影機