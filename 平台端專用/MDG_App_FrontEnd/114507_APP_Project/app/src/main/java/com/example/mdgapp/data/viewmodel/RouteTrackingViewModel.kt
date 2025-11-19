// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/RouteTrackingViewModel.kt
package com.example.mdgapp.data.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import android.location.Location
import android.util.Log
import com.example.mdgapp.data.LocationService // 匯入實際的位置服務 [cite: 1404]
import com.google.android.gms.maps.model.LatLng
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// ✅ 狀態調整為即時追蹤
data class RouteTrackingUiState(
    val totalDistance: Float = 0f,
    val time: Int = 0, // 應透過計時器實現，這裡暫時保留
    val userPath: List<LatLng> = emptyList(),
    val currentPosition: LatLng? = null, // 即時目前位置
    val startLocation: LatLng? = null,
    val endLocation: LatLng? = null,
    val isTracking: Boolean = false, // ✅ 新增：追蹤狀態
    val locationError: String? = null // 處理位置服務錯誤，例如權限問題
)

class RouteTrackingViewModel(application: Application) : AndroidViewModel(application) {

    // 實例化位置服務
    private val locationService = LocationService(application.applicationContext)
    private var trackingJob: Job? = null // 用於管理位置數據流的 Job

    private val _uiState = MutableStateFlow(RouteTrackingUiState())
    val uiState: StateFlow<RouteTrackingUiState> = _uiState.asStateFlow()

    init {
        // 移除載入模擬路線的邏輯
    }

    // ✅ 開始追蹤
    fun startTracking() {
        if (_uiState.value.isTracking) return

        // 1. 重設狀態
        _uiState.update {
            it.copy(
                isTracking = true,
                userPath = emptyList(),
                currentPosition = null,
                startLocation = null,
                endLocation = null,
                totalDistance = 0f,
                time = 0,
                locationError = null
            )
        }

        // 2. 開始收集位置更新
        trackingJob?.cancel() // 取消任何舊的 Job
        trackingJob = viewModelScope.launch {
            locationService.locationUpdates
                .catch { e ->
                    // 處理錯誤，例如權限不足
                    _uiState.update { it.copy(locationError = e.message, isTracking = false) }
                    Log.e("Tracking", "位置流錯誤: ${e.message}")
                }
                .collect { location ->
                    handleNewLocation(location)
                }
        }
    }

    // ✅ 停止追蹤
    fun stopTracking() {
        trackingJob?.cancel()
        trackingJob = null
        _uiState.update { it.copy(isTracking = false) }
        // TODO: 這裡應該加入將最終行程數據儲存到資料庫或 API 的邏輯
    }

    // ✅ 處理新的位置座標
    private fun handleNewLocation(location: Location) {
        val newLatLng = LatLng(location.latitude, location.longitude)

        _uiState.update { currentState ->
            val updatedPath = currentState.userPath + newLatLng

            // 簡易距離計算 (生產環境應使用更精確的服務)
            var distanceIncrease = 0f
            if (currentState.userPath.isNotEmpty() && currentState.userPath.size > 1) {
                val lastLocation = Location("").apply {
                    latitude = currentState.userPath.last().latitude
                    longitude = currentState.userPath.last().longitude
                }
                // distanceTo 回傳的是公尺，/ 1000f 轉成公里
                distanceIncrease = location.distanceTo(lastLocation) / 1000f
            }

            currentState.copy(
                userPath = updatedPath,
                currentPosition = newLatLng,
                startLocation = currentState.startLocation ?: newLatLng,
                endLocation = newLatLng,
                totalDistance = currentState.totalDistance + distanceIncrease,
                locationError = null
            )
        }
    }

    // 移除原有的 loadSimulatedRoute 和 getSimulatedSnappedRoute
}