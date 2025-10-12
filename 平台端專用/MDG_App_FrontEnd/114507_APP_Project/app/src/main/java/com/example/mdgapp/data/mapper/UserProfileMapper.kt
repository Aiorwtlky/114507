// 檔案路徑: app/src/main/java/com/example/mdgapp/data/mapper/UserProfileMapper.kt

package com.example.mdgapp.data.mapper

import com.example.mdgapp.data.model.NotificationSettings
import com.example.mdgapp.data.model.UserProfile
import com.example.mdgapp.data.model.UserProfileResponse

fun UserProfileResponse.toLocalUserProfile(): UserProfile {
    return UserProfile(
        fullName = "${this.lastName ?: ""}${this.firstName ?: ""}",
        employeeId = this.personnelprofile?.personnelNumber ?: "N/A",
        avatarUrl = this.personnelprofile?.avatar ?: "",
        // ✅✅✅ 關鍵修正：如果 email 是 null，就提供一個空字串作為預設值 ✅✅✅
        email = this.email ?: "",
        phone = this.personnelprofile?.phone ?: "N/A",
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