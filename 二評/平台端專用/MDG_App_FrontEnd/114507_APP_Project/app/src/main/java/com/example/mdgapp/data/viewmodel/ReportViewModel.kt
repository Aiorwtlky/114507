package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.*
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
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

    private fun generateMockReports() {
        viewModelScope.launch {
            val today = LocalDate.now()
            _reports.value = (0..6).map { dayIndex ->
                val date = today.minusDays(dayIndex.toLong())
                createMockReportForDate(date)
            }
        }
    }

    // ✅ 修正點：優化模擬資料的生成邏輯
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

        val geminiFeedback = if (generatedEvents.isEmpty()) {
            "駕駛行為良好，無明顯危險事件，請繼續保持。"
        } else {
            "偵測到 ${generatedEvents.first().eventType} 事件，請特別注意${generatedEvents.first().suggestion.substring(2)}。"
        }

        return DrivingReport(
            date = date,
            totalScore = finalScore,
            scoreRating = scoreRating,
            comparisonWithAverage = finalScore - 85, // 假設平均分為85
            geminiFeedback = geminiFeedback,
            tripInfo = TripInfo("08:31", "17:54", Random.nextDouble(80.0, 150.0), Random.nextInt(120, 300)),
            performanceMetrics = PerformanceMetrics(
                safety = (95 - totalDeduction * 0.5).toInt().coerceIn(60, 100),
                behavior = (92 - totalDeduction * 0.8).toInt().coerceIn(60, 100),
                compliance = (98 - totalDeduction * 1.2).toInt().coerceIn(60, 100),
                efficiency = Random.nextInt(85, 99)
            ),
            events = generatedEvents
        )
    }

    private fun createMockEvents(): List<DangerousEventItem> {
        val allEvents = listOf(
            DangerousEventItem("急加速", "09:15", "中", 3, "起步時請緩慢踩下油門。"),
            DangerousEventItem("疲勞駕駛", "14:32", "高", 8, "建議停車休息。"),
            DangerousEventItem("急煞車", "10:55", "中", 4, "請與前車保持安全距離。"),
            DangerousEventItem("超速", "16:20", "高", 10, "請注意道路速限。")
        )
        // 50% 的機率沒有任何事件
        if (Random.nextBoolean()) return emptyList()

        return allEvents.shuffled().take(Random.nextInt(1, 3))
    }
}