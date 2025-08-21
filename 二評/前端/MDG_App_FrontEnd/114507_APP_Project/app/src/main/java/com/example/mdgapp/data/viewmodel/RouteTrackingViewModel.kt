package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.android.gms.maps.model.LatLng
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import kotlin.math.*

data class RouteTrackingUiState(
    val totalDistance: Float = 0f,
    val time: Int = 0
)

class RouteTrackingViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(RouteTrackingUiState())
    val uiState: StateFlow<RouteTrackingUiState> = _uiState

    init {
        simulateFetchFromServer()
    }

    private fun simulateFetchFromServer() {
        viewModelScope.launch {
            delay(500) // 模擬 API 延遲
            _uiState.value = RouteTrackingUiState(
                totalDistance = 3.7f,
                time = 1320  // 22分鐘
            )
        }
    }
}


