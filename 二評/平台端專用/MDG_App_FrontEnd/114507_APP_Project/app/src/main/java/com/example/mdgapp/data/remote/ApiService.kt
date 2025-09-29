package com.example.mdgapp.data.remote

import com.example.mdgapp.data.model.Trip
import retrofit2.Response
import retrofit2.http.*
import com.google.gson.annotations.SerializedName

interface ApiService {

    // 使用者登入 (取得 Token)
    @POST("/api-token-auth/")
    suspend fun login(@Body loginRequest: LoginRequest): Response<LoginResponse>

    // 取得行程列表
    @GET("/api/trips/")
    suspend fun getTrips(@Header("Authorization") token: String): Response<List<Trip>>

}

// 為了方便，我們先把登入需要的 Request 和 Response Body 也定義在這裡
// 之後可以考慮移到 model 資料夾
data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    @SerializedName("token")
    val token: String
)