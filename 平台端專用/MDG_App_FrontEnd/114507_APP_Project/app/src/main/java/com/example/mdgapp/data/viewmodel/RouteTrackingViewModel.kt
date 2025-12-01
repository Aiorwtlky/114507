package com.example.mdgapp.data.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import android.location.Location
import com.example.mdgapp.data.SimulatedLocationService
import com.google.android.gms.maps.model.LatLng
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/**
 * 路線追蹤 UI 狀態
 */
data class RouteTrackingUiState(
    val totalDistance: Float = 0f,         // 總距離（公里）
    val time: Int = 0,                     // 總時間（秒）
    val averageSpeed: Float = 0f,          // 平均速度（公里/小時）
    val userPath: List<LatLng> = emptyList(), // 使用者路徑
    val routePath: List<LatLng> = emptyList(), // 路線路徑（用於顯示）
    val startLocation: LatLng? = null,     // 起點
    val endLocation: LatLng? = null,       // 終點
    val currentIndex: Int = 0,             // 當前位置索引（用於動畫）
    val isLoading: Boolean = false,        // 載入狀態
    val locationError: String? = null      // 錯誤訊息
)

class RouteTrackingViewModel(application: Application) : AndroidViewModel(application) {

    private val _uiState = MutableStateFlow(RouteTrackingUiState(isLoading = true))
    val uiState: StateFlow<RouteTrackingUiState> = _uiState.asStateFlow()

    private val simulatedLocationService = SimulatedLocationService()

    init {
        loadFullRoute()
    }

    /**
     * 載入完整路線資料
     */
    private fun loadFullRoute() {
        _uiState.update { it.copy(isLoading = true) }

        viewModelScope.launch {
            try {
                // 模擬載入延遲
                kotlinx.coroutines.delay(800)

                // 取得平滑的模擬路徑（smoothFactor = 3，在每兩點間插入3個點）
                val fullPath = simulatedLocationService.getSmoothSimulatedPath(smoothFactor = 3)

                // 計算統計資料
                var totalDistance = 0f
                fullPath.forEachIndexed { index, location ->
                    if (index > 0) {
                        totalDistance += location.distanceTo(fullPath[index - 1])
                    }
                }

                // 轉換為 LatLng 列表
                val latLngPath = fullPath.map { location ->
                    LatLng(location.latitude, location.longitude)
                }

                // 取得路線路徑（用於地圖顯示）
                val routePath = simulatedLocationService.getSimulatedSnappedRoute()

                val start = latLngPath.firstOrNull()
                val end = latLngPath.lastOrNull()

                // 計算總時間（秒）
                val totalTime = simulatedLocationService.getEstimatedTime()

                // 計算平均速度（公里/小時）
                val averageSpeed = if (totalTime > 0) {
                    (totalDistance / 1000f) / (totalTime / 3600f)
                } else {
                    0f
                }

                _uiState.update {
                    it.copy(
                        userPath = latLngPath,
                        routePath = routePath,
                        startLocation = start,
                        endLocation = end,
                        totalDistance = totalDistance / 1000f, // 轉換為公里
                        time = totalTime,
                        averageSpeed = averageSpeed,
                        isLoading = false,
                        locationError = null
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        locationError = "載入路線失敗：${e.message}"
                    )
                }
            }
        }
    }

    /**
     * 重新載入路線
     */
    fun reloadRoute() {
        loadFullRoute()
    }

    /**
     * 取得路線統計資訊
     */
    fun getRouteStats(): RouteStats {
        val state = _uiState.value
        return RouteStats(
            distance = state.totalDistance,
            duration = state.time,
            averageSpeed = state.averageSpeed,
            estimatedCalories = calculateCalories(state.totalDistance, state.time)
        )
    }

    /**
     * 計算消耗卡路里（簡化計算）
     */
    private fun calculateCalories(distanceKm: Float, timeSeconds: Int): Float {
        // 假設以中等速度騎車，每分鐘約消耗 5-8 卡路里
        val timeMinutes = timeSeconds / 60f
        return timeMinutes * 6.5f
    }
}

/**
 * 路線統計資料
 */
data class RouteStats(
    val distance: Float,        // 距離（公里）
    val duration: Int,          // 時長（秒）
    val averageSpeed: Float,    // 平均速度（公里/小時）
    val estimatedCalories: Float // 預估消耗卡路里
)