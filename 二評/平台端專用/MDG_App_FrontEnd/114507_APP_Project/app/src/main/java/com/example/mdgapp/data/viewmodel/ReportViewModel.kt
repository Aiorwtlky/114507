package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.Duration
import java.time.LocalDate
import java.time.LocalDateTime
import kotlin.random.Random

// ✅ 1. 在 DrivingReport 中新增 startLocation 和 endLocation
data class DrivingReport(
    val date: LocalDate,
    val totalScore: Int,
    val scoreRating: String,
    val comparisonWithAverage: Int,
    val geminiFeedback: String,
    val tripInfo: TripInfo,
    val performanceMetrics: PerformanceMetrics,
    val events: List<DangerousEventItem>,
    val startLocation: String,
    val endLocation: String
)

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

    private fun generateMockReports() {
        viewModelScope.launch {
            val today = LocalDate.now()
            _reports.value = (0..6).map { dayIndex ->
                val date = today.minusDays(dayIndex.toLong())
                createMockReportForDate(date)
            }
        }
    }

    private fun createMockReportForDate(date: LocalDate): DrivingReport {
        val baseScore = 100
        val generatedEvents = createMockEvents()
        val totalDeduction = generatedEvents.sumOf { it.deductionPoints }
        val finalScore = (baseScore - totalDeduction).coerceIn(0, 100)

        val scoreRating = when {
            finalScore >= 90 -> "優秀"
            finalScore >= 80 -> "良好"
            finalScore >= 60 -> "警告"
            else -> "危險"
        }

        val geminiFeedback = if (generatedEvents.isEmpty()) "駕駛行為良好，無明顯危險事件。" else "偵測到 ${generatedEvents.first().eventType} 事件，請特別注意。"

        val locations = listOf("台北" to "台中", "高雄" to "台南", "花蓮" to "宜蘭").random()

        return DrivingReport(
            date = date,
            totalScore = finalScore,
            scoreRating = scoreRating,
            comparisonWithAverage = finalScore - 85,
            geminiFeedback = geminiFeedback,
            tripInfo = TripInfo("08:31", "17:54", Random.nextDouble(80.0, 150.0), Random.nextInt(120, 300)),
            performanceMetrics = PerformanceMetrics( (95 - totalDeduction * 0.5).toInt().coerceIn(60, 100), (92 - totalDeduction * 0.8).toInt().coerceIn(60, 100), (98 - totalDeduction * 1.2).toInt().coerceIn(60, 100), Random.nextInt(85, 99) ),
            events = generatedEvents,
            // ✅ 2. 產生模擬資料時加入地點
            startLocation = locations.first,
            endLocation = locations.second
        )
    }

    private fun createMockEvents(): List<DangerousEventItem> {
        val allEvents = listOf(
            DangerousEventItem("急加速", "09:15", "中", 3, "起步時請緩慢踩下油門。"),
            DangerousEventItem("疲勞駕駛", "14:32", "高", 8, "建議停車休息。"),
            DangerousEventItem("急煞車", "10:55", "中", 4, "請與前車保持安全距離。"),
            DangerousEventItem("超速", "16:20", "高", 10, "請注意道路速限。")
        )
        if (Random.nextDouble() > 0.5) return emptyList()
        return allEvents.shuffled().take(Random.nextInt(1, 3))
    }
}

// ✅ 3. 新增一個擴充函式，用於將 DrivingReport 轉換為 LastTripInfo
fun DrivingReport.toLastTripInfo(): LastTripInfo {
    return LastTripInfo(
        startTime = this.date.atTime(8, 31), // 簡化範例
        endTime = this.date.atTime(17, 54),  // 簡化範例
        duration = Duration.ofMinutes(this.tripInfo.totalDurationMinutes.toLong()),
        startLocation = this.startLocation,
        endLocation = this.endLocation,
        mileage = this.tripInfo.totalDistanceKm,
        totalScore = this.totalScore,
        improvementPercentage = this.comparisonWithAverage,
        violations = this.events.map { Violation(it.eventType, it.deductionPoints) },
        aiSuggestion = this.geminiFeedback
    )
}