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

// 建議：為了保持程式碼整潔，未來可以將這個 class 獨立成一個新檔案 (e.g., ManagerReportRepository.kt)
class ManagerReportRepository {
    suspend fun getDrivers(): List<DriverInfo> {
        // TODO: 在此處呼叫 API 取得所有駕駛員列表
        return listOf(
            DriverInfo("D001", "陳大文", 92),
            DriverInfo("D007", "林美麗", 85),
            DriverInfo("D008", "張偉強", 76),
            DriverInfo("D024", "黃小玲", 98)
        )
    }

    suspend fun getReportsForDriver(driverId: String): List<DrivingReport> {
        // TODO: 在此處呼叫 API 根據 driverId 取得報表
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
            geminiFeedback = "整體駕駛平穩，請繼續保持。",
            tripInfo = TripInfo(
                startTime = "08:31",
                endTime = "17:54",
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
            DangerousEventItem("車道偏離", "11:05", "低", 1, "請將注意力集中於前方道路。"),
            DangerousEventItem("使用手機", "16:40", "高", 10, "駕駛時使用手機極度危險。"),
            DangerousEventItem("急煞車", "10:55", "中", 4, "請與前車保持安全距離。")
        )
        return allEvents.shuffled().take(Random.nextInt(1, 4))
    }
}

class ManagerReportViewModel : ViewModel() {

    private val repository = ManagerReportRepository()

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
            _drivers.value = repository.getDrivers()
        }
    }

    fun selectDriver(driverId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _selectedDriverId.value = driverId
            if (!allReportsData.containsKey(driverId)) {
                allReportsData[driverId] = repository.getReportsForDriver(driverId)
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
        // TODO: 在此處觸發真實的下載邏輯
        return message
    }
}