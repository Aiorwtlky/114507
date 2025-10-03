package com.example.mdgapp.data.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.LocalDate
import kotlin.random.Random

class ManagerReportViewModel : ViewModel() {

    private val _drivers = MutableStateFlow<List<DriverInfo>>(emptyList())
    val drivers: StateFlow<List<DriverInfo>> = _drivers.asStateFlow()

    private val _selectedDriverId = MutableStateFlow<String?>(null)

    private val _selectedDriverReports = MutableStateFlow<List<DrivingReport>>(emptyList())
    val selectedDriverReports: StateFlow<List<DrivingReport>> = _selectedDriverReports.asStateFlow()

    private val _selectedReportDetail = MutableStateFlow<DrivingReport?>(null)
    val selectedReportDetail: StateFlow<DrivingReport?> = _selectedReportDetail.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private var allReportsData: MutableMap<String, List<DrivingReport>> = mutableMapOf()

    init {
        fetchDrivers()
    }

    private fun fetchDrivers() {
        viewModelScope.launch {
            _drivers.value = getMockDrivers()
        }
    }

    fun selectDriver(driverId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _selectedDriverId.value = driverId
            if (!allReportsData.containsKey(driverId)) {
                allReportsData[driverId] = getMockReportsForDriver(driverId)
            }
            _selectedDriverReports.value = allReportsData[driverId] ?: emptyList()
            _isLoading.value = false
        }
    }

    fun selectReportByDate(date: LocalDate) {
        val currentDriverId = _selectedDriverId.value
        if (currentDriverId != null) {
            _selectedReportDetail.value = allReportsData[currentDriverId]?.find { it.date == date }
        }
    }

    fun downloadReportForDriver(report: DrivingReport, driver: DriverInfo): String {
        val message = "開始為 ${driver.driverName} 下載 ${report.date} 的報表..."
        Log.d("ManagerReport", message)
        return message
    }

    // --- 模擬資料產生邏輯 ---
    private fun getMockDrivers(): List<DriverInfo> {
        return listOf(
            DriverInfo("D001", "陳大文", 92),
            DriverInfo("D007", "林美麗", 85),
            DriverInfo("D008", "張偉強", 76),
            DriverInfo("D024", "黃小玲", 98)
        )
    }

    private fun getMockReportsForDriver(driverId: String): List<DrivingReport> {
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
        return DrivingReport(
            date = date,
            totalScore = score,
            scoreRating = scoreRating,
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