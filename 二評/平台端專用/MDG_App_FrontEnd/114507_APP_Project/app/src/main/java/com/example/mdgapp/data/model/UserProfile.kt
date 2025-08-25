package com.example.mdgapp.data.model

// 代表一個已連結的外部平台帳號
data class LinkedAccount(
    val platform: String, // 例如 "Google", "Apple"
    val username: String, // 例如 "johndoe@gmail.com"
    val iconResId: Int // 平台圖示的資源 ID
)

// 代表完整的用戶個人資料
data class UserProfile(
    val fullName: String,
    val employeeId: String,
    val avatarUrl: String, // 暫用 URL 字串，未來可改為圖片資源
    val currentVehiclePlate: String,
    val groupName: String,
    val email: String,
    val phone: String,
    val licenseNumber: String,
    val licenseClass: String,
    val linkedAccounts: List<LinkedAccount>,
    val notificationSettings: NotificationSettings
)

// 通知設定
data class NotificationSettings(
    var receiveDangerousEvent: Boolean,
    var receiveSystemAnnouncements: Boolean,
    var downloadOnlyOnWifi: Boolean
)
