package com.example.mdgapp.data.model

import kotlinx.serialization.Serializable

@Serializable // <-- 務必確認存在
data class UserProfile(
    val fullName: String,
    val employeeId: String,
    val avatarUrl: String,
    val currentVehiclePlate: String,
    val groupName: String,
    val nfcCardNumber: String,
    val email: String,
    val phone: String,
    val licenseNumber: String,
    val licenseClass: String,
    val linkedAccounts: List<LinkedAccount>,
    val notificationSettings: NotificationSettings
)

@Serializable // <-- 務必確認存在
data class LinkedAccount(
    val platform: String,
    val username: String,
    val iconResId: Int
)

@Serializable // <-- 務必確認存在
data class NotificationSettings(
    val receiveDangerousEvent: Boolean,
    val receiveSystemAnnouncements: Boolean,
    val downloadOnlyOnWifi: Boolean
)