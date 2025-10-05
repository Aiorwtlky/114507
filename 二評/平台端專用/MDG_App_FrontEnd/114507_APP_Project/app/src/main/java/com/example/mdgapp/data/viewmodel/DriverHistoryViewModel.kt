package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.random.Random

// ✅ 1. 簡化 UiState，移除不再需要的圖表相關欄位
data class DriverHistoryUiState(
    val totalMileage: Int = 0,
    val totalDurationHours: Int = 0,
    val totalTrips: Int = 0,
    val lifetimeAverageScore: Int = 0,
    val topEvents: List<Pair<String, Int>> = emptyList(),
    val totalEvents: Int = 0,
    val isLoading: Boolean = true
)

class DriverHistoryViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(DriverHistoryUiState())
    val uiState: StateFlow<DriverHistoryUiState> = _uiState.asStateFlow()

    init {
        // ✅ 2. 初始化時只呼叫一次數據產生函式
        fetchRealisticDashboardStats()
    }

    // ✅ 3. 建立一個產生更真實數據的函式
    private fun fetchRealisticDashboardStats() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            // 模擬一位駕駛員大約一年的數據
            val totalTrips = Random.nextInt(220, 260) // 一年大約出車 240 趟
            val averageDistancePerTrip = Random.nextDouble(150.0, 300.0) // 每次長途的平均距離
            val totalMileage = (totalTrips * averageDistancePerTrip).toInt()
            val totalDurationHours = (totalMileage / Random.nextDouble(60.0, 75.0)).toInt() // 平均時速在 60-75 之間
            val lifetimeAverageScore = Random.nextInt(82, 91)

            // 模擬違規事件的分佈
            val fatigueCount = Random.nextInt(15, 30)
            val speedingCount = Random.nextInt(10, 25)
            val phoneUsageCount = Random.nextInt(5, 15)
            val harshBrakingCount = Random.nextInt(20, 40)

            val topEventsData = listOf(
                "疲勞駕駛" to fatigueCount,
                "超速" to speedingCount,
                "使用手機" to phoneUsageCount,
                "急煞車" to harshBrakingCount
            ).sortedByDescending { it.second }.take(3) // 取出前三名

            val totalEventsData = fatigueCount + speedingCount + phoneUsageCount + harshBrakingCount

            _uiState.update {
                it.copy(
                    totalMileage = totalMileage,
                    totalDurationHours = totalDurationHours,
                    totalTrips = totalTrips,
                    lifetimeAverageScore = lifetimeAverageScore,
                    topEvents = topEventsData,
                    totalEvents = totalEventsData,
                    isLoading = false
                )
            }
        }
    }
}