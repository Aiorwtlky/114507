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
                // ✅ 注意：我們將 today 傳入，以便判斷是否為最新一筆
                val date = today.minusDays(dayIndex.toLong())
                createMockReportForDate(date, today)
            }
        }
    }

    // ✅ 修改 createMockReportForDate 函式，使其能產生更真實的長途數據
    private fun createMockReportForDate(date: LocalDate, today: LocalDate): DrivingReport {
        // 如果是最新一筆報告 (today)，就產生固定的長途行程
        if (date == today) {
            val longHaulEvents = listOf(
                DangerousEventItem("超速", "10:30", "高", 8, "偵測到在國道一號苗栗路段超速，請注意速限。"),
                DangerousEventItem("疲勞駕駛", "14:15", "高", 10, "系統偵測到您已長時間駕駛，建議於下個服務區休息。")
            )
            val totalDeduction = longHaulEvents.sumOf { it.deductionPoints }
            val finalScore = (100 - totalDeduction)

            return DrivingReport(
                date = date,
                totalScore = finalScore,
                scoreRating = "良好",
                comparisonWithAverage = finalScore - 85, // 假設車隊平均為85分
                geminiFeedback = "長途駕駛辛苦了。本次偵測到超速與疲勞駕駛事件，為了安全，請務必定時休息並遵守交通規則。",
                tripInfo = TripInfo(
                    startTime = "07:30",
                    endTime = "13:45",
                    totalDistanceKm = 365.5, // 台北到高雄的合理公里數
                    totalDurationMinutes = 375 // 約6小時15分，包含短暫休息
                ),
                performanceMetrics = PerformanceMetrics(
                    safety = 85,
                    behavior = 88,
                    compliance = 78,
                    efficiency = 92
                ),
                events = longHaulEvents,
                startLocation = "台北市南港區",
                endLocation = "高雄市左營區"
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
                comparisonWithAverage = finalScore - 85,
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