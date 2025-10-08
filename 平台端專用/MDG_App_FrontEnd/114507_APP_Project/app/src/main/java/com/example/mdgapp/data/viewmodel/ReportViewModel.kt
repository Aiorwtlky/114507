package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.DangerousEventItem
import com.example.mdgapp.data.model.DrivingReport
import com.example.mdgapp.data.model.PerformanceMetrics
import com.example.mdgapp.data.model.TripInfo
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.LocalDate
import kotlin.random.Random

class ReportViewModel : ViewModel() {

    private val _reports = MutableStateFlow<List<DrivingReport>>(emptyList())
    val reports: StateFlow<List<DrivingReport>> = _reports.asStateFlow()

    private val _selectedReport = MutableStateFlow<DrivingReport?>(null)
    val selectedReport: StateFlow<DrivingReport?> = _selectedReport.asStateFlow()

    init {
        generateMockReports()
    }

    fun selectReportByDate(date: LocalDate) {
        _selectedReport.value = _reports.value.find { it.date == date }
    }

    fun generateMockReports() {
        viewModelScope.launch {
            val today = LocalDate.now()
            _reports.value = (0..6).map { dayIndex ->
                val date = today.minusDays(dayIndex.toLong())
                createMockReportForDate(date, today)
            }
        }
    }

    private fun createMockReportForDate(date: LocalDate, today: LocalDate): DrivingReport {
        // 如果是最新一筆報告 (today)，就產生固定的中長途行程
        if (date == today) {
            val longHaulEvents = listOf(
                DangerousEventItem("急加速", "09:45", "中", 4, "偵測到在國道一號南崁交流道加速過快。"),
                DangerousEventItem("急煞車", "11:05", "低", 2, "接近台中港區時車速過快導致急煞。")
            )
            val totalDeduction = longHaulEvents.sumOf { it.deductionPoints }
            val finalScore = (100 - totalDeduction)

            return DrivingReport(
                date = date,
                totalScore = finalScore,
                scoreRating = "優秀",
                comparisonWithAverage = finalScore - 88, // 假設車隊平均為88分
                geminiFeedback = "本次行程路線規劃良好，僅有零星的急加速與急煞車事件，整體表現優異。",
                tripInfo = TripInfo(
                    startTime = "09:30",
                    endTime = "11:20",
                    totalDistanceKm = 135.8, // 桃園機場到台中港的合理公里數
                    totalDurationMinutes = 110 // 約1小時50分鐘
                ),
                performanceMetrics = PerformanceMetrics(
                    safety = 92,
                    behavior = 95,
                    compliance = 90,
                    efficiency = 94
                ),
                events = longHaulEvents,
                startLocation = "桃園機場貨運站",
                endLocation = "台中港"
            )
        } else {
            // 過往的報告則維持隨機產生
            val generatedEvents = createMockEventsForPast()
            val totalDeduction = generatedEvents.sumOf { it.deductionPoints }
            val finalScore = (100 - totalDeduction).coerceIn(0, 100)
            val scoreRating = when {
                finalScore >= 90 -> "優秀"
                finalScore >= 80 -> "良好"
                else -> "警告"
            }
            val locations = listOf("台中港" to "基隆港", "桃園機場" to "台中市區", "花蓮市" to "台東市").random()

            return DrivingReport(
                date = date,
                totalScore = finalScore,
                scoreRating = scoreRating,
                comparisonWithAverage = finalScore - 88,
                geminiFeedback = if (generatedEvents.isEmpty()) "駕駛行為良好。" else "偵測到 ${generatedEvents.first().eventType} 事件。",
                tripInfo = TripInfo("09:10", "16:45", Random.nextDouble(150.0, 250.0), Random.nextInt(200, 360)),
                performanceMetrics = PerformanceMetrics(
                    (95 - totalDeduction * 0.5).toInt().coerceIn(60, 100),
                    (92 - totalDeduction * 0.8).toInt().coerceIn(60, 100),
                    (98 - totalDeduction * 1.2).toInt().coerceIn(60, 100),
                    Random.nextInt(85, 99)
                ),
                events = generatedEvents,
                startLocation = locations.first,
                endLocation = locations.second
            )
        }
    }

    private fun createMockEventsForPast(): List<DangerousEventItem> {
        val allEvents = listOf(
            DangerousEventItem("急加速", "09:15", "中", 3, "起步時請緩慢踩下油門。"),
            DangerousEventItem("急煞車", "10:55", "中", 4, "請與前車保持安全距離。")
        )
        if (Random.nextDouble() > 0.6) return emptyList()
        return allEvents.shuffled().take(Random.nextInt(1, 2))
    }
}