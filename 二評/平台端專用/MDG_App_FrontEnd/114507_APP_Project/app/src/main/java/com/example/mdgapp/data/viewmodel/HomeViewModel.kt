// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/HomeViewModel.kt

package com.example.mdgapp.data.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.toLastTripInfo
import com.example.mdgapp.data.remote.ApiService
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.Duration
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
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
    private val apiService: ApiService = RetrofitInstance.api

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        initialize()
    }

    private fun initialize() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            try {
                // AuthInterceptor 會在背景自動從 TokenManager 取得 Token 並加入請求中
                val response = apiService.getTrips()

                if (response.isSuccessful) {
                    val trips = response.body()
                    val lastTrip = trips?.firstOrNull()?.toLastTripInfo()

                    _uiState.update {
                        it.copy(
                            lastTrip = lastTrip,
                            isLoading = false
                        )
                    }
                } else {
                    Log.e("HomeViewModel", "取得行程列表失敗: ${response.code()}")
                    _uiState.update { it.copy(isLoading = false) }
                }

            } catch (e: Exception) {
                Log.e("HomeViewModel", "初始化時發生錯誤", e)
                _uiState.update { it.copy(isLoading = false) }
            }

            onAverageTimeUnitSelected("月")
            onTrendTimeUnitSelected("月")
        }
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