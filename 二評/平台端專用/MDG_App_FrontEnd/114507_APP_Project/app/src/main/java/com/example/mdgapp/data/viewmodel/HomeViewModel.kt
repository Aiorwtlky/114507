// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/HomeViewModel.kt

package com.example.mdgapp.data.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.toLastTripInfo // 👈 【重點】匯入我們剛建立的 Mapper
import com.example.mdgapp.data.remote.ApiService
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.Duration
import java.time.LocalDateTime
import kotlin.random.Random

// ... LastTripInfo, Violation, PastAverageData, PastTrendData, HomeUiState 這些 data class 保持不變 ...
// (這裡省略，以節省篇幅)

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


//  classe HomeViewModel(
//     // 👈 【重點】1. 使用建構式注入 (Constructor Injection) 傳入 ApiService
//     // 這樣可以讓 ViewModel 和網路層解耦，也方便未來進行單元測試
//     private val apiService: ApiService
// ) : ViewModel() {
class HomeViewModel : ViewModel() {
    private val apiService: ApiService = RetrofitInstance.api

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        initialize()
    }

    private fun initialize() {
        // 👈 【重點】2. 這裡是修改的核心
        viewModelScope.launch {
            // 在發起請求前，先顯示讀取中狀態
            _uiState.update { it.copy(isLoading = true) }

            try {
                // TODO: Token 應該從 SharedPreferences 或 DataStore 中安全地讀取
                // 這裡我們先用一個假 token 示範
                val token = "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

                // 發起真實的 API 請求
                val response = apiService.getTrips(token)

                if (response.isSuccessful) {
                    val trips = response.body()
                    // 取得列表中的第一筆作為最新行程，並進行轉換
                    val lastTrip = trips?.firstOrNull()?.toLastTripInfo()

                    _uiState.update {
                        it.copy(
                            lastTrip = lastTrip,
                            isLoading = false // 成功後，結束讀取狀態
                        )
                    }
                } else {
                    // API 請求失敗 (e.g., 401, 404, 500)
                    Log.e("HomeViewModel", "取得行程列表失敗: ${response.code()}")
                    _uiState.update { it.copy(isLoading = false) } // 失敗後，也要結束讀取狀態
                }

            } catch (e: Exception) {
                // 網路連線錯誤或其他例外
                Log.e("HomeViewModel", "初始化時發生錯誤", e)
                _uiState.update { it.copy(isLoading = false) } // 發生例外，也要結束讀取狀態
            }

            // 這兩行保持不變，因為它們是控制「過往平均」和「過往趨勢」的 UI
            // 且它們目前仍是使用模擬資料
            onAverageTimeUnitSelected("月")
            onTrendTimeUnitSelected("月")
        }
    }

    // --- 以下的函式 (過往平均、過往趨勢) 都不需要變動 ---
    // --- (省略，以節省篇幅) ---
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