// 檔案路徑: app/src/main/java/com/example/mdgapp/data/remote/ApiService.kt

package com.example.mdgapp.data.remote

import com.example.mdgapp.data.model.Trip
import com.example.mdgapp.data.model.LoginRequest
import com.example.mdgapp.data.model.LoginResponse
import com.example.mdgapp.data.model.RegisterRequest
import com.example.mdgapp.data.model.RegisterResponse
import retrofit2.Response
import com.example.mdgapp.data.model.TripDetail // 👈 匯入新的資料模型
import retrofit2.http.Path // 👈 匯入 @Path
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface ApiService {

    // 使用者登入 (取得 Token)
    @POST("/api-token-auth/")
    suspend fun login(@Body loginRequest: LoginRequest): Response<LoginResponse>

    // 使用者註冊
    @POST("/api/register/")
    suspend fun registerUser(@Body request: RegisterRequest): Response<RegisterResponse>

    // 取得行程列表
    @GET("/api/trips/")
    suspend fun getTrips(): Response<List<Trip>>

    @GET("/api/trips/{id}/")
    suspend fun getTripDetails(@Path("id") tripId: Int): Response<TripDetail>
}