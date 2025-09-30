// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/ManagerReportViewModel.kt

package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.DriverInfo
import com.example.mdgapp.data.model.Trip
import com.example.mdgapp.data.model.TripDetail
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ManagerReportViewModel : ViewModel() {

    private val apiService = RetrofitInstance.api

    // 駕駛員列表，暫時仍使用模擬資料，因為 API 尚未提供
    private val _drivers = MutableStateFlow<List<DriverInfo>>(emptyList())
    val drivers: StateFlow<List<DriverInfo>> = _drivers.asStateFlow()

    // 【修改】報表列表的型別改為 List<Trip>
    private val _selectedDriverReports = MutableStateFlow<List<Trip>>(emptyList())
    val selectedDriverReports: StateFlow<List<Trip>> = _selectedDriverReports.asStateFlow()

    // 【修改】報表詳情的型別改為 TripDetail? 以便與 ReportDetailScreen 共用
    private val _selectedReportDetail = MutableStateFlow<TripDetail?>(null)
    val selectedReportDetail: StateFlow<TripDetail?> = _selectedReportDetail.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    init {
        fetchDrivers()
    }

    private fun fetchDrivers() {
        viewModelScope.launch {
            // TODO: 未來需替換為真實的 API 呼叫
            _drivers.value = listOf(
                DriverInfo("D001", "陳大文", 92),
                DriverInfo("D007", "林美麗", 85)
            )
        }
    }

    // 當管理者選擇一位駕駛時
    fun selectDriver(driverId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            // TODO: API 更新後，這裡應傳入 driverId 來獲取指定駕駛的行程
            // 目前暫時先獲取管理者自己的行程列表作為替代
            try {
                val response = apiService.getTrips()
                if(response.isSuccessful) {
                    _selectedDriverReports.value = response.body() ?: emptyList()
                }
            } catch (e: Exception) {
                // 錯誤處理
            }
            _isLoading.value = false
        }
    }

    // 【新增】獲取單筆行程詳情的函式
    fun fetchTripDetails(tripId: Int) {
        _selectedReportDetail.value = null // 開始獲取前先清空，以顯示讀取動畫
        viewModelScope.launch {
            try {
                val response = apiService.getTripDetails(tripId)
                if (response.isSuccessful) {
                    _selectedReportDetail.value = response.body()
                }
            } catch (e: Exception) {
                // 錯誤處理
            }
        }
    }
}