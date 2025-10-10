package com.example.mdgapp.data.remote

import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit

object RetrofitInstance {

    private const val BASE_URL = "http://140.131.114.182:8000/"

    private val json = Json {
        ignoreUnknownKeys = true
    }

    // ⭐ 1. 取得信任所有憑證的 OkHttpClient Builder
    private val unsafeOkHttpClientBuilder = getUnsafeOkHttpClientBuilder()

    // ⭐ 2. 在這個 Builder 上加入您的攔截器
    private val client = unsafeOkHttpClientBuilder
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        })
        .addInterceptor(AuthInterceptor())
        .build()

    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client) // ⭐ 3. 使用我們新建的 client
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
    }

    val api: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }
}