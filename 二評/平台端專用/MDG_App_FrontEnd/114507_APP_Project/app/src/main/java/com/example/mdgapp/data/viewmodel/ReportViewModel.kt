// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/ReportViewModel.kt

package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.Trip
import com.example.mdgapp.data.model.TripDetail
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ReportViewModel : ViewModel() {

    private val apiService = RetrofitInstance.api

    // 用於報表列表，持有 Trip 的摘要列表
    private val _reports = MutableStateFlow<List<Trip>>(emptyList())
    val reports: StateFlow<List<Trip>> = _reports.asStateFlow()

    // 用於報表詳情，只持有當前選中的那一筆 TripDetail
    private val _selectedReport = MutableStateFlow<TripDetail?>(null)
    val selectedReport: StateFlow<TripDetail?> = _selectedReport.asStateFlow()

    init {
        fetchReports()
    }

    // 獲取行程摘要列表 (用於 ReportListScreen)
    fun fetchReports() {
        viewModelScope.launch {
            try {
                val response = apiService.getTrips()
                if (response.isSuccessful) {
                    _reports.value = response.body() ?: emptyList()
                }
            } catch (e: Exception) {
                // 處理錯誤
            }
        }
    }

    // 根據 ID 獲取單筆行程的詳細資料 (用於 ReportDetailScreen)
    fun fetchTripDetails(tripId: Int) {
        // 在開始獲取前，先清空舊資料，讓 UI 顯示讀取動畫
        _selectedReport.value = null
        viewModelScope.launch {
            try {
                val response = apiService.getTripDetails(tripId)
                if (response.isSuccessful) {
                    _selectedReport.value = response.body()
                }
            } catch (e: Exception) {
                // 處理錯誤
            }
        }
    }
}