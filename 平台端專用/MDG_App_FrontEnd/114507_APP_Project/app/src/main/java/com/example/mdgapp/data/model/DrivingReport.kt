package com.example.mdgapp.data.model

import java.time.LocalDate

// 代表一份完整的每日駕駛報告
data class DrivingReport(
    val date: LocalDate,
    val totalScore: Int,
    val scoreRating: String, // 例如: "優異", "良好", "待改進"
    val comparisonWithAverage: Int, // 與平均分的差異, e.g., 5, -3
    val geminiFeedback: String,
    val tripInfo: TripInfo,
    val performanceMetrics: PerformanceMetrics,
    val events: List<DangerousEventItem>,
    // ✅ 新增欄位
    val startLocation: String,
    val endLocation: String
)

// 行程基本資訊
data class TripInfo(
    val startTime: String,
    val endTime: String,
    val totalDistanceKm: Double,
    val totalDurationMinutes: Int
)

// 各項表現指標分數
data class PerformanceMetrics(
    val safety: Int,
    val behavior: Int,
    val compliance: Int,
    val efficiency: Int
)

// 單一危險事件項目
data class DangerousEventItem(
    val eventType: String,
    val time: String,
    val severity: String, // "高", "中", "低"
    val deductionPoints: Int,
    val suggestion: String
)