package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.Duration
import java.time.LocalDateTime
import kotlin.random.Random

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
        initialize()
    }

    private fun initialize() {
        viewModelScope.launch {
            delay(1500) // 模擬網路請求

            val now = LocalDateTime.now()
            val mockLastTrip = LastTripInfo(
                startTime = now.minusHours(2),
                endTime = now.minusHours(1),
                duration = Duration.ofHours(1),
                startLocation = "台北市中正區",
                endLocation = "新北市林口區",
                mileage = 25.3,
                totalScore = 88,
                improvementPercentage = 5,
                violations = listOf(
                    Violation("急加速", -5),
                    Violation("超速", -7)
                ),
                aiSuggestion = "林口交流道前請提早切換車道，避免急煞。"
            )

            _uiState.update {
                it.copy(
                    lastTrip = mockLastTrip,
                    isLoading = false
                )
            }
            // 初始化時，直接觸發時間單位選擇事件，就會自動載入最新的值
            onAverageTimeUnitSelected("月")
            onTrendTimeUnitSelected("月")
        }
    }

    // --- 過往平均 ---
    fun onAverageTimeUnitSelected(timeUnit: String) {
        val newValueOptions = generateValueOptions(timeUnit)
        // 自動選擇最新的值 (列表中的第一個)
        val selectedValue = newValueOptions.firstOrNull() ?: ""
        val newScore = Random.nextInt(75, 95)

        _uiState.update { currentState ->
            currentState.copy(
                pastAverage = currentState.pastAverage.copy(
                    selectedTimeUnit = timeUnit,
                    valueOptions = newValueOptions,
                    selectedValue = selectedValue,
                    averageScore = newScore
                )
            )
        }
    }

    fun onAverageValueSelected(value: String) {
        // 只更新選擇的值和分數
        val newScore = Random.nextInt(75, 95)
        _uiState.update { currentState ->
            currentState.copy(
                pastAverage = currentState.pastAverage.copy(
                    selectedValue = value,
                    averageScore = newScore
                )
            )
        }
    }

    // --- 過往趨勢 ---
    fun onTrendTimeUnitSelected(timeUnit: String) {
        val newValueOptions = generateValueOptions(timeUnit)
        // 自動選擇最新的值 (列表中的第一個)
        val selectedValue = newValueOptions.firstOrNull() ?: ""
        val (data, labels) = generateChartData(timeUnit)

        _uiState.update { currentState ->
            currentState.copy(
                pastTrend = currentState.pastTrend.copy(
                    selectedTimeUnit = timeUnit,
                    valueOptions = newValueOptions,
                    selectedValue = selectedValue,
                    chartData = data,
                    chartLabels = labels
                )
            )
        }
    }

    fun onTrendValueSelected(value: String) {
        // 只更新選擇的值和圖表數據
        // 這裡可以根據 value 模擬不同數據，為簡化，我們先保持不變
        _uiState.update { currentState ->
            currentState.copy(
                pastTrend = currentState.pastTrend.copy(
                    selectedValue = value
                )
            )
        }
    }

    private fun generateValueOptions(timeUnit: String): List<String> {
        val now = LocalDateTime.now()
        return when (timeUnit) {
            "年" -> (0..2).map { (now.year - it).toString() + "年" }
            // ✅ 修正 #3: 移除季度和月份中的年份顯示
            "季" -> {
                val currentQuarter = (now.monthValue - 1) / 3 + 1
                (0..3).map {
                    val q = (currentQuarter - 1 - it + 4) % 4 + 1
                    "第${q}季"
                }
            }
            "月" -> {
                (0..5).map { now.minusMonths(it.toLong()).monthValue.toString() + "月" }
            }
            else -> emptyList()
        }
    }

    private fun generateChartData(timeUnit: String): Pair<List<Int>, List<String>> {
        return when (timeUnit) {
            "年" -> {
                val data = (1..12).map { Random.nextInt(75, 96) }
                val labels = (1..12).map { "${it}月" }
                data to labels
            }
            "季" -> {
                val data = (1..13).map { Random.nextInt(70, 96) }
                val labels = (0..12).map { "W${it + 1}" }
                data to labels
            }
            else -> { // 月
                val data = (1..30).map { Random.nextInt(68, 99) }
                val labels = (1..30).map { it.toString() }
                data to labels
            }
        }
    }
}