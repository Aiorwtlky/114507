// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/RouteTrackingViewModel.kt
package com.example.mdgapp.data.viewmodel

import android.app.Application
import android.location.Location
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.LocationService
import com.example.mdgapp.data.SimulatedLocationService
import com.google.android.gms.maps.model.LatLng
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class RouteTrackingUiState(
    val totalDistance: Float = 0f,
    val time: Int = 0,
    val isTracking: Boolean = false,
    val userPath: List<LatLng> = emptyList(),
    val currentLocation: LatLng? = null
)

class RouteTrackingViewModel(application: Application) : AndroidViewModel(application) {

    // ✅ 開關：設為 true 來使用模擬數據，設為 false 使用真實 GPS
    private val useSimulation = true

    private val _uiState = MutableStateFlow(RouteTrackingUiState())
    val uiState: StateFlow<RouteTrackingUiState> = _uiState.asStateFlow()

    private val realLocationService = LocationService(application)
    private val simulatedLocationService = SimulatedLocationService()
    private var locationJob: Job? = null
    private var timerJob: Job? = null

    fun toggleTracking() {
        if (_uiState.value.isTracking) {
            stopTracking()
        } else {
            startTracking()
        }
    }

    private fun startTracking() {
        _uiState.update {
            it.copy(
                isTracking = true,
                userPath = emptyList(),
                totalDistance = 0f,
                time = 0
            )
        }
        startTimer()
        startLocationUpdates()
    }

    private fun stopTracking() {
        _uiState.update { it.copy(isTracking = false) }
        locationJob?.cancel()
        timerJob?.cancel()
    }

    private fun startTimer() {
        timerJob = viewModelScope.launch {
            while (_uiState.value.isTracking) {
                delay(1000)
                _uiState.update { it.copy(time = it.time + 1) }
            }
        }
    }

    private fun startLocationUpdates() {
        val locationFlow = if (useSimulation) {
            simulatedLocationService.locationUpdates
        } else {
            realLocationService.locationUpdates
        }

        locationJob = locationFlow
            .catch { e ->
                e.printStackTrace()
            }
            .onEach { location ->
                val newLatLng = LatLng(location.latitude, location.longitude)
                _uiState.update { currentState ->
                    val newPath = currentState.userPath + newLatLng
                    val newDistance = if (newPath.size > 1) {
                        currentState.totalDistance + calculateDistance(newPath[newPath.size - 2], newLatLng)
                    } else {
                        0f
                    }
                    currentState.copy(
                        currentLocation = newLatLng,
                        userPath = newPath,
                        totalDistance = newDistance
                    )
                }
            }
            .launchIn(viewModelScope)
    }

    private fun calculateDistance(start: LatLng, end: LatLng): Float {
        val results = FloatArray(1)
        Location.distanceBetween(
            start.latitude, start.longitude,
            end.latitude, end.longitude,
            results
        )
        return results[0] / 1000 // 轉換為公里
    }

    override fun onCleared() {
        super.onCleared()
        stopTracking()
    }
}