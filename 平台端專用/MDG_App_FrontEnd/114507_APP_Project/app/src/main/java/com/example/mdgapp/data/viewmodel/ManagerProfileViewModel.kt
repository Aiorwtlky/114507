package com.example.mdgapp.data.viewmodel
/*
import androidx.lifecycle.ViewModel
import com.example.mdgapp.R
import com.example.mdgapp.data.model.LinkedAccount
import com.example.mdgapp.data.model.NotificationSettings
import com.example.mdgapp.data.model.UserProfile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class ManagerProfileViewModel : ViewModel() {

    private val _userProfile = MutableStateFlow<UserProfile?>(null)
    val userProfile: StateFlow<UserProfile?> = _userProfile.asStateFlow()

    init {
        // ✅ 修正：直接呼叫同步載入函式
        loadManagerProfile()
    }

    // ✅ 修正：將原本的非同步載入 (fetch) 改為同步載入 (load)
    private fun loadManagerProfile() {
        // 直接、同步地建立 UserProfile 物件，移除 viewModelScope 和 delay
        _userProfile.value = UserProfile(
            fullName = "王大明 (管理者)",
            employeeId = "MGR-001",
            email = "manager.wang@example.com",
            phone = "0987-654-321",
            avatarUrl = "", // 確保 avatarUrl 欄位存在
            currentVehiclePlate = "N/A (管理帳號)",
            groupName = "總部車隊",
            licenseNumber = "A12345678",
            licenseClass = "普通小型車",
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
    }

    fun onSettingChanged(event: Boolean? = null, announcement: Boolean? = null, wifiOnly: Boolean? = null) {
        // TODO: 實作管理者設定變更的邏輯
    }
}*/