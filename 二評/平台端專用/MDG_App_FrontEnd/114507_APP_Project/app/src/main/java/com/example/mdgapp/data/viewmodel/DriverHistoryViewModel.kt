package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.TextStyle
import java.util.Locale
import kotlin.random.Random

// UiState 中新增圖表X軸標籤的欄位
data class DriverHistoryUiState(
    val totalMileage: Int = 0,
    val totalDurationHours: Int = 0,
    val totalTrips: Int = 0,
    val lifetimeAverageScore: Int = 0,
    val topEvents: List<Pair<String, Int>> = emptyList(),
    val totalEvents: Int = 0,
    val chartData: List<Int> = emptyList(),
    // ✅ 優化 3：新增X軸標籤的狀態
    val chartXAxisLabels: List<String> = emptyList(),
    val isLoading: Boolean = true,
    val timeUnitOptions: List<String> = listOf("月", "季", "年", "日"),
    val selectedTimeUnit: String = "月",
    val valueOptions: List<String> = emptyList(),
    val selectedValue: String = ""
)

class DriverHistoryViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(DriverHistoryUiState())
    val uiState: StateFlow<DriverHistoryUiState> = _uiState.asStateFlow()

    // ✅ 優化 1：定義一個包含所有時間單位的常數列表
    private val allTimeUnits = listOf("月", "季", "年", "日")

    init {
        fetchDashboardStats()
        onTimeUnitSelected("月")
    }

    // ... fetchDashboardStats 保持不變 ...
    private fun fetchDashboardStats() {
        viewModelScope.launch {
            val topEventsData = listOf("疲勞駕駛" to 15, "使用手機" to 9, "急加速" to 5)
            val totalEventsData = topEventsData.sumOf { it.second }
            _uiState.update {
                it.copy(
                    totalMileage = 12850,
                    totalDurationHours = 315,
                    totalTrips = 241,
                    lifetimeAverageScore = 88,
                    topEvents = topEventsData,
                    totalEvents = totalEventsData
                )
            }
        }
    }

    fun onTimeUnitSelected(timeUnit: String) {
        val now = LocalDate.now()
        // ✅ 優化 2：更新第二個選單的顯示邏輯
        val newValueOptions = when (timeUnit) {
            "年" -> (0..2).map { (now.year - it).toString() } // 只顯示年份數字
            "季" -> (0..3).map { "第 ${4 - it} 季" }
            "月" -> (0..5).map { now.minusMonths(it.toLong()).monthValue.toString() + "月" }
            "日" -> (0..6).map { now.minusDays(it.toLong()).dayOfMonth.toString() + "日" }
            else -> emptyList()
        }
        _uiState.update {
            it.copy(
                selectedTimeUnit = timeUnit,
                valueOptions = newValueOptions,
                selectedValue = newValueOptions.firstOrNull() ?: "",
                // ✅ 優化 1：更新第一個選單的選項，移除當前已選中的項目
                timeUnitOptions = allTimeUnits.filter { option -> option != timeUnit }
            )
        }
        fetchChartData()
    }

    fun onValueSelected(value: String) {
        _uiState.update { it.copy(selectedValue = value) }
        fetchChartData()
    }

    private fun fetchChartData() {
        viewModelScope.launch {
            val currentState = _uiState.value

            // ✅ 優化 3：產生更平滑的模擬數據和對應的X軸標籤
            var currentScore = (80..90).random()
            val newChartData = mutableListOf<Int>()
            val newLabels = mutableListOf<String>()

            val (dataPoints, labels) = when (currentState.selectedTimeUnit) {
                "年" -> 12 to (1..12).map { "${it}月" }
                "季" -> 12 to (1..12).map { "W${it}" }
                "月" -> 30 to (1..30).map { "${it}" }
                "日" -> 24 to (0..23).map { "${it}h" }
                else -> 0 to emptyList()
            }

            repeat(dataPoints) {
                currentScore += Random.nextInt(-3, 4) // 分數在-3到+3之間隨機波動
                newChartData.add(currentScore.coerceIn(60, 100)) // 確保分數在60-100之間
            }
            newLabels.addAll(labels)

            _uiState.update { it.copy(chartData = newChartData, chartXAxisLabels = newLabels, isLoading = false) }
        }
    }
}