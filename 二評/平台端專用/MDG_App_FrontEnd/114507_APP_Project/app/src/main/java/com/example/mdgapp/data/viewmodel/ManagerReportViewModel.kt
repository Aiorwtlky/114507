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

// 管理者專用的 ViewModel
class ManagerReportViewModel : ViewModel() {

    // ... (狀態宣告部分保持不變) ...
    private val _drivers = MutableStateFlow<List<DriverInfo>>(emptyList())
    val drivers: StateFlow<List<DriverInfo>> = _drivers.asStateFlow()

    private val _selectedDriverReports = MutableStateFlow<List<DrivingReport>>(emptyList())
    val selectedDriverReports: StateFlow<List<DrivingReport>> = _selectedDriverReports.asStateFlow()

    private val _selectedReportDetail = MutableStateFlow<DrivingReport?>(null)
    val selectedReportDetail: StateFlow<DrivingReport?> = _selectedReportDetail.asStateFlow()

    private var allReportsData: Map<String, List<DrivingReport>> = emptyMap()

    init {
        generateMockDataForAllDrivers()
    }

    // ... (selectDriver, selectReportByDate, downloadReportForDriver 函式保持不變) ...
    fun selectDriver(driverId: String) {
        _selectedDriverReports.value = allReportsData[driverId] ?: emptyList()
    }

    fun selectReportByDate(date: LocalDate) {
        _selectedReportDetail.value = _selectedDriverReports.value.find { it.date == date }
    }

    fun downloadReportForDriver(report: DrivingReport, driver: DriverInfo): String {
        val message = "開始為 ${driver.driverName} 下載 ${report.date} 的報表..."
        Log.d("ManagerReport", message)
        return message
    }

    // === Mock Data Generation ===

    private fun generateMockDataForAllDrivers() {
        viewModelScope.launch {
            val driverIdAndNames = mapOf(
                "D001" to "陳大文",
                "D007" to "林美麗",
                "D008" to "張偉強",
                "D024" to "黃小玲"
            )

            // 1. 先為每位駕駛員生成一周的報表數據
            val reportMap = mutableMapOf<String, List<DrivingReport>>()
            driverIdAndNames.keys.forEach { driverId ->
                val today = LocalDate.now()
                reportMap[driverId] = (0..6).map { dayIndex ->
                    val date = today.minusDays(dayIndex.toLong())
                    createMockReportForDate(date)
                }
            }
            allReportsData = reportMap

            // ✅ 優化 1：根據已生成的報表來建立駕駛列表，確保分數一致
            // 2. 根據剛生成的報表數據，建立駕駛員列表
            val driverList = driverIdAndNames.map { (id, name) ->
                // 從報表Map中找到該駕駛的報表列表，並取得最新一筆（第一筆）的分數
                val latestScore = allReportsData[id]?.firstOrNull()?.totalScore ?: 0
                DriverInfo(
                    driverId = id,
                    driverName = name,
                    latestScore = latestScore // 使用報表中的真實分數
                )
            }
            _drivers.value = driverList
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
            // ✅ 優化 2：呼叫 createMockEvents() 來生成事件紀錄
            events = createMockEvents()
        )
    }

    // ✅ 優化 2：新增此函式以生成模擬的危險事件
    private fun createMockEvents(): List<DangerousEventItem> {
        val allEvents = listOf(
            DangerousEventItem("急加速", "09:15", "中", 3, "起步時請緩慢踩下油門，避免車輛頓挫。"),
            DangerousEventItem("疲勞駕駛", "14:32", "高", 8, "偵測到您眼皮閉合時間過長，建議停車休息。"),
            DangerousEventItem("車道偏離", "11:05", "低", 1, "請將注意力集中於前方道路，確保行駛於車道中央。"),
            DangerousEventItem("使用手機", "16:40", "高", 10, "駕駛時使用手機極度危險，請使用藍牙耳機或停車後再操作。"),
            DangerousEventItem("急煞車", "10:55", "中", 4, "請與前車保持安全距離，預留足夠的反應時間。")
        )
        // 隨機取 1 到 3 筆事件
        return allEvents.shuffled().take(Random.nextInt(1, 4))
    }
}