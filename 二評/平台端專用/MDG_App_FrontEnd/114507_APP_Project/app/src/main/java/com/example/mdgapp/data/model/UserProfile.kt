package com.example.mdgapp.data.model

data class UserProfile(
    val fullName: String,
    val employeeId: String,
    val avatarUrl: String,
    val currentVehiclePlate: String,
    val groupName: String,
    val nfcCardNumber: String, // ✅ 新增 NFC 卡號欄位
    val email: String,
    val phone: String,
    val licenseNumber: String,
    val licenseClass: String,
    val linkedAccounts: List<LinkedAccount>,
    val notificationSettings: NotificationSettings
)

data class LinkedAccount(
    val platform: String,
    val username: String,
    val iconResId: Int
)

data class NotificationSettings(
    val receiveDangerousEvent: Boolean,
    val receiveSystemAnnouncements: Boolean,
    val downloadOnlyOnWifi: Boolean
)