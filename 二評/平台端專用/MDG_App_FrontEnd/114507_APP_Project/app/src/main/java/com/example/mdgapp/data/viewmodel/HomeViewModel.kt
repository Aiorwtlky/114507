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

// =================================================================================
// Data Class 定義
// =================================================================================

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


// =================================================================================
// ViewModel 實作
// =================================================================================

class HomeViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        initialize()
    }

    private fun initialize() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            delay(1000) // 模擬網路延遲

            val mockLastTrip = generateRandomLastTrip()

            _uiState.update {
                it.copy(
                    lastTrip = mockLastTrip,
                    isLoading = false
                )
            }

            // 初始化圖表資料
            onAverageTimeUnitSelected("月")
            onTrendTimeUnitSelected("月")
        }
    }

    private fun generateRandomLastTrip(): LastTripInfo {
        // --- 隨機參數設定 ---
        val baseScore = 100
        val possibleViolations = listOf(
            Violation("急加速", -5) to "偵測到多次急加速，請平穩起步以節省油耗。",
            Violation("急煞車", -7) to "與前車距離過近導致急煞，請保持安全車距。",
            Violation("超速", -10) to "在市區道路有超速紀錄，請注意速限。",
            Violation("疲勞駕駛", -8) to "偵測到疲勞跡象，建議稍作休息再上路。"
        )
        val locations = listOf(
            "台北車站" to "桃園機場",
            "新竹科學園區" to "台中市區",
            "高雄港" to "台南市中心",
            "花蓮市" to "太魯閣"
        )

        // --- 產生隨機數據 ---
        val selectedViolations = if (Random.nextBoolean()) {
            possibleViolations.shuffled().take(Random.nextInt(1, 3))
        } else {
            emptyList()
        }

        val totalDeduction = selectedViolations.sumOf { it.first.scoreDeduction }
        val finalScore = (baseScore + totalDeduction).coerceIn(0, 100)

        val aiSuggestion = if (selectedViolations.isEmpty()) {
            "本次行程表現優秀，無任何違規紀錄。"
        } else {
            selectedViolations.random().second
        }

        val (start, end) = locations.random()
        val durationMinutes = Random.nextLong(30, 180)

        return LastTripInfo(
            startTime = LocalDateTime.now().minusMinutes(durationMinutes + Random.nextLong(30, 120)),
            endTime = LocalDateTime.now().minusMinutes(Random.nextLong(15, 29)),
            duration = Duration.ofMinutes(durationMinutes),
            startLocation = start,
            endLocation = end,
            mileage = Random.nextDouble(25.0, 200.0).roundTo(1),
            totalScore = finalScore,
            improvementPercentage = if (finalScore > 85) Random.nextInt(1, 11) else Random.nextInt(-5, 5),
            violations = selectedViolations.map { it.first },
            aiSuggestion = aiSuggestion
        )
    }

    fun onAverageTimeUnitSelected(timeUnit: String) {
        val newValueOptions = generateValueOptions(timeUnit)
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

    fun onTrendTimeUnitSelected(timeUnit: String) {
        val newValueOptions = generateValueOptions(timeUnit)
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
        val (data, labels) = generateChartData(_uiState.value.pastTrend.selectedTimeUnit)
        _uiState.update { currentState ->
            currentState.copy(
                pastTrend = currentState.pastTrend.copy(
                    selectedValue = value,
                    chartData = data,
                    chartLabels = labels
                )
            )
        }
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

private fun Double.roundTo(decimals: Int): Double {
    var multiplier = 1.0
    repeat(decimals) { multiplier *= 10 }
    return kotlin.math.round(this * multiplier) / multiplier
}