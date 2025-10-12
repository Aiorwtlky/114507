// 檔案路徑: app/src/main/java/com/example/mdgapp/data/model/UserProfileResponse.kt

package com.example.mdgapp.data.model

// ✅ 1. 匯入 kotlinx.serialization 的工具
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName

// ✅ 2. 為每個需要序列化的 data class 加上 @Serializable 註解
@Serializable
data class UserProfileResponse(
    val id: Int?,
    val username: String?,
    // ✅ 3. 使用 @SerialName 處理命名不一致的問題
    @SerialName("last_login")
    val lastLogin: String?,
    @SerialName("first_name")
    val firstName: String?,
    @SerialName("last_name")
    val lastName: String?,
    val email: String?,
    @SerialName("is_staff")
    val isStaff: Boolean?,
    @SerialName("personnelprofile")
    val personnelprofile: PersonnelProfile?
)

@Serializable
data class PersonnelProfile(
    @SerialName("personnel_number")
    val personnelNumber: String?,
    val gender: String?,
    @SerialName("license_number")
    val licenseNumber: String?,
    val avatar: String?,
    val phone: String?,
    @SerialName("license_type")
    val licenseType: String?,
    @SerialName("driving_experience")
    val drivingExperience: Int?,
    @SerialName("nfc_card_id")
    val nfcCardId: String?
)