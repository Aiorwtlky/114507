package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter
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

    // --- 模擬資料生成 ---
    private fun createMockReportForDate(date: LocalDate): DrivingReport {
        val score = Random.nextInt(75, 99)
        return DrivingReport(
            date = date,
            totalScore = score,
            scoreRating = if (score > 90) "優異" else if (score > 80) "良好" else "待改進",
            comparisonWithAverage = Random.nextInt(-5, 6),
            geminiFeedback = listOf(
                "整體駕駛平穩，請繼續保持。",
                "偵測到數次急加速，請注意油門控制。",
                "有輕微疲勞駕駛跡象，請確保休息充足。"
            ).random(),
            tripInfo = TripInfo(
                startTime = "08:31", endTime = "17:54",
                totalDistanceKm = Random.nextDouble(80.0, 150.0),
                totalDurationMinutes = Random.nextInt(120, 300)
            ),
            performanceMetrics = PerformanceMetrics(
                safety = Random.nextInt(80, 101),
                behavior = Random.nextInt(70, 96),
                compliance = Random.nextInt(90, 101),
                efficiency = Random.nextInt(75, 99)
            ),
            events = createMockEvents()
        )
    }

    private fun createMockEvents(): List<DangerousEventItem> {
        val allEvents = listOf(
            DangerousEventItem("急加速", "09:15", "中", 3, "起步時請緩慢踩下油門，避免車輛頓挫。"),
            DangerousEventItem("疲勞駕駛", "14:32", "高", 8, "偵測到您眼皮閉合時間過長，建議停車休息。"),
            DangerousEventItem("車道偏離", "11:05", "低", 1, "請將注意力集中於前方道路，確保行駛於車道中央。"),
            DangerousEventItem("使用手機", "16:40", "高", 10, "駕駛時使用手機極度危險，請使用藍牙耳機或停車後再操作。"),
            DangerousEventItem("急煞車", "10:55", "中", 4, "請與前車保持安全距離，預留足夠的反應時間。")
        )
        return allEvents.shuffled().take(Random.nextInt(1, 4))
    }
}
