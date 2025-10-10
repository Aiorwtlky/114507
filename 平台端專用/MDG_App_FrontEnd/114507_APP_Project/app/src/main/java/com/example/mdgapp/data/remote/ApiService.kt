package com.example.mdgapp.data.remote

import com.example.mdgapp.data.model.LoginRequest
import com.example.mdgapp.data.model.LoginResponse
import com.example.mdgapp.data.model.NfcBindRequest
import com.example.mdgapp.data.model.NfcBindResponse
import com.example.mdgapp.data.model.UserProfileResponse
import com.example.mdgapp.data.model.*
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
interface ApiService {

    @POST("api/token/")
    suspend fun loginUser(@Body loginRequest: LoginRequest): LoginResponse

    // ⭐ 修正：移除 @Header 參數
    @GET("api/auth/profile/")
    suspend fun getUserProfile(): UserProfileResponse

    // ⭐ 修正：移除 @Header 參數
    @POST("api/auth/profile/bind-nfc/")
    suspend fun bindNfcCard(
        @Body nfcBindRequest: NfcBindRequest
    ): NfcBindResponse

    @GET("api/health/")
    suspend fun healthCheck(): HealthCheckResponse
}