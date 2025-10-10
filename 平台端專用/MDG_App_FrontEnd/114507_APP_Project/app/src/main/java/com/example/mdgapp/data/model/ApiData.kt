package com.example.mdgapp.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// ⭐ 功能 1: 使用者登入
@Serializable
data class LoginRequest(
    val username: String,
    val password: String
)

@Serializable
data class LoginResponse(
    val access: String,
    val refresh: String
)


// ⭐ 功能 2: 取得使用者 Profile
@Serializable
data class UserProfileResponse(
    val id: Int,
    val username: String,
    @SerialName("first_name") val firstName: String,
    @SerialName("last_name") val lastName: String,
    val email: String,
    @SerialName("is_staff") val isStaff: Boolean,
    @SerialName("is_group_leader") val isGroupLeader: Boolean,
    @SerialName("administered_groups") val administeredGroups: List<Int>,
    val personnelprofile: PersonnelProfileResponse?
)

@Serializable
data class PersonnelProfileResponse(
    @SerialName("personnel_number") val personnelNumber: String,
    val gender: String,
    @SerialName("license_number") val licenseNumber: String?,
    val avatar: String?,
    val phone: String?,
    @SerialName("license_type") val licenseType: String?,
    @SerialName("driving_experience") val drivingExperience: Int
)


// ⭐ 功能 3: 綁定 NFC
@Serializable
data class NfcBindRequest(
    @SerialName("nfc_id") val nfcId: String
)

@Serializable
data class NfcBindResponse(
    val success: String
)

@Serializable
data class HealthCheckResponse(
    val status: String,
    val database: String,
    @SerialName("ai_service") val aiService: String
)