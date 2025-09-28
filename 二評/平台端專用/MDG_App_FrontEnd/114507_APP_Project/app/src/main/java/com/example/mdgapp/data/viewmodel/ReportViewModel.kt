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

// 步驟 1: 建立一個倉儲類別 (Repository) 來處理資料來源
class ReportRepository {
    // 模擬的 API 呼叫
    suspend fun getReportsForCurrentUser(): List<DrivingReport> {
        // TODO: 在此處呼叫您的後端 API
        // 以下是模擬資料
        val today = LocalDate.now()
        return (0..6).map { dayIndex ->
            val date = today.minusDays(dayIndex.toLong())
            createMockReportForDate(date)
        }
    }

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

// 步驟 2: 修改 ViewModel，讓它從 Repository 取得資料
class ReportViewModel : ViewModel() {

    private val repository = ReportRepository() // 實際專案中，這裡會透過依賴注入 (DI) 傳入

    private val _reports = MutableStateFlow<List<DrivingReport>>(emptyList())
    val reports: StateFlow<List<DrivingReport>> = _reports.asStateFlow()

    private val _selectedReport = MutableStateFlow<DrivingReport?>(null)
    val selectedReport: StateFlow<DrivingReport?> = _selectedReport.asStateFlow()

    init {
        fetchReports()
    }

    private fun fetchReports() {
        viewModelScope.launch {
            // 透過 repository 取得資料
            _reports.value = repository.getReportsForCurrentUser()
        }
    }

    fun selectReportByDate(date: LocalDate) {
        // 這部分的邏輯是正確的
        _selectedReport.value = _reports.value.find { it.date == date }
    }
}