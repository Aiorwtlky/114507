package com.example.mdgapp.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

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


@Serializable
data class PersonnelProfileResponse(
    @SerialName("personnel_number") val personnelNumber: String?,
    val gender: String?,
    @SerialName("license_number") val licenseNumber: String?,
    val avatar: String?,
    val phone: String?,
    @SerialName("license_type") val licenseType: String?,
    @SerialName("driving_experience") val drivingExperience: Int?,

    // ⭐ 修正重點：在欄位後面加上 `= null`，提供一個預設值
    @SerialName("nfc_card_id") val nfcCardId: String? = null
)

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