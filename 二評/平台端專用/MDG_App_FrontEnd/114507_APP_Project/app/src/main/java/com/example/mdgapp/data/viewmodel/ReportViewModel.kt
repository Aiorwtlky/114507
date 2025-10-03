package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.LocalDate
import kotlin.random.Random

// Repository 已被移除，ViewModel 直接負責產生模擬資料
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

    // 將輔助函式放回 ViewModel 中
    private fun createMockReportForDate(date: LocalDate): DrivingReport {
        val score = Random.nextInt(55, 101)
        val scoreRating = when {
            score >= 90 -> "優秀"
            score >= 80 -> "良好"
            score >= 60 -> "警告"
            else -> "危險"
        }
        return DrivingReport(date, score, scoreRating, Random.nextInt(-5, 6), "整體駕駛平穩，請繼續保持。",
            TripInfo("08:31", "17:54", Random.nextDouble(80.0, 150.0), Random.nextInt(120, 300)),
            PerformanceMetrics(Random.nextInt(80, 101), Random.nextInt(70, 96), Random.nextInt(90, 101), Random.nextInt(75, 99)),
            createMockEvents()
        )
    }

    private fun createMockEvents(): List<DangerousEventItem> {
        val allEvents = listOf(
            DangerousEventItem("急加速", "09:15", "中", 3, "起步時請緩慢踩下油門。"),
            DangerousEventItem("疲勞駕駛", "14:32", "高", 8, "建議停車休息。")
        )
        return allEvents.shuffled().take(Random.nextInt(1, 3))
    }
}