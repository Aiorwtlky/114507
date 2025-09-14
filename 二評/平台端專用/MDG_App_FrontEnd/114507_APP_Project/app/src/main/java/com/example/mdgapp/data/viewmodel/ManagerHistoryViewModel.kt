package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.DriverInfo
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// 用於包裝管理者儀表板所有數據的資料類別
data class ManagerHistoryUiState(
    // 核心數據
    val fleetAverageScore: Int = 0,
    val topRiskFactor: String = "",
    val highRiskDriverCount: Int = 0,
    val criticalEventsThisMonth: Int = 0,
    // 排名列表
    val bestPerformingDrivers: List<DriverInfo> = emptyList(),
    val driversNeedingAttention: List<DriverInfo> = emptyList(),
    // 圖表數據
    val chartData: List<Int> = emptyList(),
    val chartXAxisLabels: List<String> = emptyList(),
    val isLoading: Boolean = true
)

class ManagerHistoryViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(ManagerHistoryUiState())
    val uiState: StateFlow<ManagerHistoryUiState> = _uiState.asStateFlow()

    init {
        fetchManagerHistoryData()
    }

    private fun fetchManagerHistoryData() {
        viewModelScope.launch {
            // 模擬網路或資料庫讀取延遲
            delay(1500)

            // 模擬從資料庫撈取並計算後的數據
            _uiState.update {
                it.copy(
                    fleetAverageScore = 82,
                    topRiskFactor = "疲勞駕駛",
                    highRiskDriverCount = 1,
                    criticalEventsThisMonth = 4,
                    bestPerformingDrivers = listOf(
                        DriverInfo("D008", "張偉強", 95),
                        DriverInfo("D001", "陳大文", 91),
                        DriverInfo("D007", "林美麗", 84)
                    ),
                    driversNeedingAttention = listOf(
                        DriverInfo("D024", "黃小玲", 68)
                    ),
                    chartData = listOf(85, 83, 86, 82, 84, 81, 79, 83),
                    chartXAxisLabels = listOf("W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"),
                    isLoading = false
                )
            }
        }
    }
}