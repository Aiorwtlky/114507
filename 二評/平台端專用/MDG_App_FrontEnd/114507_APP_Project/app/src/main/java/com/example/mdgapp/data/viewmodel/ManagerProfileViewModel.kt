package com.example.mdgapp.data.viewmodel

// ✅ 新增 import：解決 Unresolved reference 'Log' 錯誤
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.R
import com.example.mdgapp.data.model.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ManagerProfileViewModel : ViewModel() {

    private val _userProfile = MutableStateFlow<UserProfile?>(null)
    val userProfile: StateFlow<UserProfile?> = _userProfile.asStateFlow()

    init {
        fetchManagerProfile()
    }

    private fun fetchManagerProfile() {
        viewModelScope.launch {
            try {
                delay(500)
                _userProfile.value = UserProfile(
                    fullName = "王大明 (管理者)",
                    employeeId = "MGR-001",
                    email = "manager.wang@example.com",
                    phone = "0987-654-321",
                    currentVehiclePlate = "N/A (管理帳號)",
                    groupName = "總部車隊",
                    licenseNumber = "A12345678",
                    licenseClass = "普通小型車",
                    avatarUrl = "",
                    linkedAccounts = listOf(
                        LinkedAccount("Google", "manager.wang@gmail.com", R.drawable.ic_google),
                        LinkedAccount("Apple", "manager.wang@me.com", R.drawable.ic_apple)
                    ),
                    notificationSettings = NotificationSettings(
                        receiveDangerousEvent = true,
                        receiveSystemAnnouncements = true,
                        downloadOnlyOnWifi = false
                    )
                )
            } catch (e: Exception) {
                // 如果 UserProfile 的結構不對，這裡會捕捉到錯誤並印出 log
                Log.e("ManagerProfileVM", "Error fetching profile", e)
            }
        }
    }

    fun onSettingChanged(event: Boolean? = null, announcement: Boolean? = null, wifiOnly: Boolean? = null) {
        // TODO: 實作管理者設定變更的邏輯
    }
}