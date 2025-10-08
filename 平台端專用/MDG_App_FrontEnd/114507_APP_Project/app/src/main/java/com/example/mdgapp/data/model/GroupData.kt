package com.example.mdgapp.data.model

import java.time.LocalDate

// --- Data Models for Group Management ---

data class GroupInfo(
    val groupName: String,
    val unitName: String,
    val leaderName: String
)

data class GroupMember(
    val id: String,
    val avatarResId: Int,
    val memberId: String,
    val name: String,
    val averageScore: Int,
    val joinDate: LocalDate,
    val status: String
)