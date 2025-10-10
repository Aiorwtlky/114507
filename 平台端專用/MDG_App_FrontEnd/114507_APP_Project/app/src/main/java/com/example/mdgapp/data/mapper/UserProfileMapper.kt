package com.example.mdgapp.data.mapper

import com.example.mdgapp.data.model.NotificationSettings
import com.example.mdgapp.data.model.UserProfile
import com.example.mdgapp.data.model.UserProfileResponse

/**
 * 擴充函式：將從 API 獲取的 UserProfileResponse 轉換為 NFC 寫入所需的本地 UserProfile 模型。
 */
fun UserProfileResponse.toLocalUserProfile(): UserProfile {
    return UserProfile(
        fullName = "${this.lastName ?: ""}${this.firstName ?: ""}",
        employeeId = this.personnelprofile?.personnelNumber ?: "N/A",
        avatarUrl = this.personnelprofile?.avatar ?: "",
        email = this.email,
        phone = this.personnelprofile?.phone ?: "N/A",
        // 注意：以下欄位在 UserProfileResponse 中不存在，暫時給予預設值
        currentVehiclePlate = "MDG-0000",
        groupName = "總部第一車隊",
        nfcCardNumber = "NFC-暫存",
        licenseNumber = this.personnelprofile?.licenseNumber ?: "N/A",
        licenseClass = this.personnelprofile?.licenseType ?: "N/A",
        linkedAccounts = emptyList(),
        notificationSettings = NotificationSettings(
            receiveDangerousEvent = true,
            receiveSystemAnnouncements = true,
            downloadOnlyOnWifi = true
        )
    )
}