// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/RouteTrackingViewModel.kt
package com.example.mdgapp.data.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.google.android.gms.maps.model.LatLng
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// ✅ 簡化 UiState，移除即時追蹤相關的狀態
data class RouteTrackingUiState(
    val totalDistance: Float = 0f,
    val time: Int = 0,
    val userPath: List<LatLng> = emptyList(),
    val startLocation: LatLng? = null,
    val endLocation: LatLng? = null
)

class RouteTrackingViewModel(application: Application) : AndroidViewModel(application) {

    private val _uiState = MutableStateFlow(RouteTrackingUiState())
    val uiState: StateFlow<RouteTrackingUiState> = _uiState.asStateFlow()

    init {
        // ✅ ViewModel 初始化時，直接載入模擬路線
        loadSimulatedRoute()
    }

    private fun loadSimulatedRoute() {
        viewModelScope.launch {
            val simulatedPath = getSimulatedSnappedRoute()
            if (simulatedPath.isNotEmpty()) {
                _uiState.update {
                    it.copy(
                        userPath = simulatedPath,
                        startLocation = simulatedPath.first(),
                        endLocation = simulatedPath.last(),
                        totalDistance = 3.7f, // 預設的模擬數據
                        time = 1320           // 預設的模擬數據 (22分鐘)
                    )
                }
            }
        }
    }

    /**
     * 模擬從 Roads API 獲取到的已校準路線
     * 這些點位會非常貼合實際道路
     */
    private fun getSimulatedSnappedRoute(): List<LatLng> {
        // 這是一條從「台北車站」經由「仁愛路」到「台北市政府」的模擬路徑
        return listOf(
            LatLng(25.0479, 121.5170), // 台北車站
            LatLng(25.0464, 121.5218), // 中山南路
            LatLng(25.0423, 121.5222), // 景福門 (圓環)
            LatLng(25.0418, 121.5288), // 仁愛路一段
            LatLng(25.0405, 121.5361),
            LatLng(25.0392, 121.5434), // 仁愛路三段
            LatLng(25.0381, 121.5501),
            LatLng(25.0370, 121.5568), // 仁愛路四段
            LatLng(25.0368, 121.5606),
            LatLng(25.0372, 121.5645)  // 台北市政府
        )
    }
}