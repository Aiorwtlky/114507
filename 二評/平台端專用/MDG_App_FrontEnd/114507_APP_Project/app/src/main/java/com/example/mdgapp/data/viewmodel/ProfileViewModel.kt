package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import com.example.mdgapp.R
import com.example.mdgapp.data.model.LinkedAccount
import com.example.mdgapp.data.model.NotificationSettings
import com.example.mdgapp.data.model.UserProfile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

class ProfileViewModel : ViewModel() {

    private val _userProfile = MutableStateFlow<UserProfile?>(null)
    val userProfile: StateFlow<UserProfile?> = _userProfile.asStateFlow()

    init {
        loadUserProfile()
    }

    private fun loadUserProfile() {
        // 模擬從網路或資料庫載入資料
        _userProfile.value = UserProfile(
            fullName = "季博達",
            employeeId = "EMP-12345",
            avatarUrl = "...", // 之後可替換為真實圖片
            currentVehiclePlate = "ABC-1234",
            groupName = "第一車隊",
            email = "jbd@example.com",
            phone = "0912-345-678",
            licenseNumber = "A123456789",
            licenseClass = "職業大客車",
            linkedAccounts = listOf(
                LinkedAccount("Google", "jbd.work@google.com", R.drawable.ic_google), // 假設您有這些圖示
                LinkedAccount("Apple", "jbd.personal@icloud.com", R.drawable.ic_apple)
            ),
            notificationSettings = NotificationSettings(
                receiveDangerousEvent = true,
                receiveSystemAnnouncements = true,
                downloadOnlyOnWifi = false
            )
        )
    }

    // 更新通知設定的方法
    fun onSettingChanged(
        event: Boolean? = null,
        announcement: Boolean? = null,
        wifiOnly: Boolean? = null
    ) {
        _userProfile.update { currentProfile ->
            currentProfile?.copy(
                notificationSettings = currentProfile.notificationSettings.copy(
                    receiveDangerousEvent = event ?: currentProfile.notificationSettings.receiveDangerousEvent,
                    receiveSystemAnnouncements = announcement ?: currentProfile.notificationSettings.receiveSystemAnnouncements,
                    downloadOnlyOnWifi = wifiOnly ?: currentProfile.notificationSettings.downloadOnlyOnWifi
                )
            )
        }
    }
}
