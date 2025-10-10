// 檔案路徑: app/src/main/java/com/example/mdgapp/data/model/AuthData.kt
/*
package com.example.mdgapp.data.model

import com.google.gson.annotations.SerializedName

/**
 * 註冊請求的資料結構，對應 API 的 Request Body
 */
data class RegisterRequest(
    @SerializedName("username")
    val username: String,

    @SerializedName("password")
    val password: String,

    @SerializedName("email")
    val email: String,

    @SerializedName("first_name")
    val firstName: String,

    @SerializedName("last_name")
    val lastName: String,

    @SerializedName("personnelprofile")
    val personnelProfile: PersonnelProfileRequest
)

/**
 * 註冊請求中，個人資料的巢狀物件
 */
data class PersonnelProfileRequest(
    @SerializedName("personnel_number")
    val personnelNumber: String,

    @SerializedName("gender")
    val gender: String, // "MALE", "FEMALE", "UNSPECIFIED"

    @SerializedName("license_number")
    val licenseNumber: String
)

/**
 * 註冊成功後的回應資料結構，對應 API 的 Success Response
 */
data class RegisterResponse(
    @SerializedName("username")
    val username: String,

    @SerializedName("email")
    val email: String,

    @SerializedName("first_name")
    val firstName: String,

    @SerializedName("last_name")
    val lastName: String,

    @SerializedName("personnelprofile")
    val personnelProfile: PersonnelProfileResponse
)

data class PersonnelProfileResponse(
    @SerializedName("personnel_number")
    val personnelNumber: String,

    @SerializedName("gender")
    val gender: String,

    @SerializedName("license_number")
    val licenseNumber: String
)

// 為了方便，我們先把登入需要的 Request 和 Response Body 也定義在這裡
// 之後可以考慮移到 model 資料夾
data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    @SerializedName("token")
    val token: String
)*/