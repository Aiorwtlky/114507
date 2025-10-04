package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.DrivingReport
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.Duration
import java.time.LocalDateTime
import kotlin.random.Random

// Data Class 定義
data class LastTripInfo(
    val startTime: LocalDateTime,
    val endTime: LocalDateTime,
    val duration: Duration,
    val startLocation: String,
    val endLocation: String,
    val mileage: Double,
    val totalScore: Int,
    val improvementPercentage: Int,
    val violations: List<Violation>,
    val aiSuggestion: String
)

data class Violation(
    val item: String,
    val scoreDeduction: Int
)

data class PastAverageData(
    val timeUnitOptions: List<String> = listOf("年", "季", "月"),
    val selectedTimeUnit: String = "月",
    val valueOptions: List<String> = emptyList(),
    val selectedValue: String = "",
    val averageScore: Int = 0
)

data class PastTrendData(
    val timeUnitOptions: List<String> = listOf("年", "季", "月"),
    val selectedTimeUnit: String = "月",
    val valueOptions: List<String> = emptyList(),
    val selectedValue: String = "",
    val chartData: List<Int> = emptyList(),
    val chartLabels: List<String> = emptyList()
)

data class HomeUiState(
    val lastTrip: LastTripInfo? = null,
    val pastAverage: PastAverageData = PastAverageData(),
    val pastTrend: PastTrendData = PastTrendData(),
    val isLoading: Boolean = true
)


class HomeViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        initializeCharts()
    }

    private fun initializeCharts() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            delay(100) // 縮短延遲，因為只載入圖表
            onAverageTimeUnitSelected("月")
            onTrendTimeUnitSelected("月")
            _uiState.update { it.copy(isLoading = false) }
        }
    }

    // 新增一個公開函式，用於接收外部傳來的最新報表
    fun setLastTrip(report: DrivingReport) {
        _uiState.update {
            it.copy(lastTrip = report.toLastTripInfo())
        }
    }

    // --- 圖表相關函式 ---
    fun onAverageTimeUnitSelected(timeUnit: String) {
        val newValueOptions = generateValueOptions(timeUnit)
        val selectedValue = newValueOptions.firstOrNull() ?: ""
        val newScore = Random.nextInt(75, 95)
        _uiState.update { it.copy(pastAverage = it.pastAverage.copy(selectedTimeUnit = timeUnit, valueOptions = newValueOptions, selectedValue = selectedValue, averageScore = newScore)) }
    }

    fun onAverageValueSelected(value: String) {
        val newScore = Random.nextInt(75, 95)
        _uiState.update { it.copy(pastAverage = it.pastAverage.copy(selectedValue = value, averageScore = newScore)) }
    }

    fun onTrendTimeUnitSelected(timeUnit: String) {
        val newValueOptions = generateValueOptions(timeUnit)
        val selectedValue = newValueOptions.firstOrNull() ?: ""
        val (data, labels) = generateChartData(timeUnit)
        _uiState.update { it.copy(pastTrend = it.pastTrend.copy(selectedTimeUnit = timeUnit, valueOptions = newValueOptions, selectedValue = selectedValue, chartData = data, chartLabels = labels)) }
    }

    fun onTrendValueSelected(value: String) {
        val (data, labels) = generateChartData(_uiState.value.pastTrend.selectedTimeUnit)
        _uiState.update { it.copy(pastTrend = it.pastTrend.copy(selectedValue = value, chartData = data, chartLabels = labels)) }
    }

    private fun generateValueOptions(timeUnit: String): List<String> {
        val now = LocalDateTime.now()
        return when (timeUnit) {
            "年" -> (0..2).map { (now.year - it).toString() + "年" }
            "季" -> {
                val currentQuarter = (now.monthValue - 1) / 3 + 1
                (0..3).map {
                    val q = (currentQuarter - 1 - it + 4) % 4 + 1
                    "第${q}季"
                }
            }
            "月" -> (0..5).map { now.minusMonths(it.toLong()).monthValue.toString() + "月" }
            else -> emptyList()
        }
    }

    private fun generateChartData(timeUnit: String): Pair<List<Int>, List<String>> {
        return when (timeUnit) {
            "年" -> (1..12).map { Random.nextInt(75, 96) } to (1..12).map { "${it}月" }
            "季" -> (1..13).map { Random.nextInt(70, 96) } to (0..12).map { "W${it + 1}" }
            else -> (1..30).map { Random.nextInt(68, 99) } to (1..30).map { it.toString() }
        }
    }
}