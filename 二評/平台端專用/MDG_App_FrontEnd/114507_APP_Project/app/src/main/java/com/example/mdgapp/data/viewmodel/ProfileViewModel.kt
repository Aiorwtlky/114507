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
    // ✅ 修正此處的變數名稱大小寫
    val userProfile: StateFlow<UserProfile?> = _userProfile.asStateFlow()

    init {
        loadUserProfile()
    }

    private fun loadUserProfile() {
        _userProfile.value = UserProfile(
            fullName = "Member 1",
            employeeId = "MDG-001",
            avatarUrl = "", // 留空，UI 層將使用預設圖示
            currentVehiclePlate = "MDG-6688",
            groupName = "總部第一車隊",
            email = "MDGDriver@gmail.com",
            phone = "0988-666-888",
            licenseNumber = "T123456789",
            licenseClass = "職業聯結車",
            linkedAccounts = listOf(
                LinkedAccount("Google", "MDGDriver@gmail.com", R.drawable.ic_google)
            ),
            notificationSettings = NotificationSettings(
                receiveDangerousEvent = true,
                receiveSystemAnnouncements = true,
                downloadOnlyOnWifi = false
            )
        )
    }

    // 更新通知設定的方法 (保持不變)
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