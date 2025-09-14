package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.random.Random

// ✅ 修正 1：在 UiState 中加入 chartXAxisLabels 欄位
data class ManagerHomeUiState(
    val onlineDrivers: Int = 0,
    val fleetAverageScore: Int = 0,
    val tripsToday: Int = 0,
    val eventsToday: Int = 0,
    val selectedTab: String = "週",
    val chartData: List<Int> = emptyList(),
    val chartXAxisLabels: List<String> = emptyList(), // 新增此行
    val isLoading: Boolean = true
)

class ManagerHomeViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(ManagerHomeUiState())
    val uiState: StateFlow<ManagerHomeUiState> = _uiState.asStateFlow()

    init {
        fetchDashboardData()
    }

    private fun fetchDashboardData() {
        viewModelScope.launch {
            delay(1000)
            _uiState.update {
                it.copy(
                    onlineDrivers = 15,
                    fleetAverageScore = 82,
                    tripsToday = 128,
                    eventsToday = 3,
                    isLoading = false
                )
            }
            onTabSelected("週")
        }
    }

    fun onTabSelected(tab: String) {
        viewModelScope.launch {
            val (newData, newLabels) = when (tab) {
                "月" -> (1..30).map { Random.nextInt(70, 95) } to (1..30).map { it.toString() }
                "週" -> (1..7).map { Random.nextInt(75, 98) } to listOf("一", "二", "三", "四", "五", "六", "日")
                "日" -> (1..24).map { Random.nextInt(65, 99) } to (0..23).map { "${it}h" }
                else -> emptyList<Int>() to emptyList<String>()
            }
            _uiState.update {
                it.copy(
                    selectedTab = tab,
                    chartData = newData,
                    chartXAxisLabels = newLabels // 更新標籤
                )
            }
        }
    }
}