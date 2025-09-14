package com.example.mdgapp.data.model

// 新增檔案：用於在管理者列表中代表一個駕駛員
data class DriverInfo(
    val driverId: String,
    val driverName: String,
    val latestScore: Int,
    val avatarUrl: String? = null // 未來可擴充頭像
)