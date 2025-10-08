// 檔案路徑: app/src/main/java/com/example/mdgapp/data/remote/RetrofitInstance.kt

package com.example.mdgapp.data.remote

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitInstance {

    // 從 API 文件來的主機位置
    private const val BASE_URL = "http://140.131.114.182/"

    // 建立一個日誌攔截器，方便在 Logcat 中看到詳細的網路請求資訊
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    // 建立 OkHttp 客戶端，並加入日誌攔截器和我們自訂的認證攔截器
    private val client = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .addInterceptor(AuthInterceptor()) // 👈 【重點】加上這一行
        .build()

    // 透過懶加載 (by lazy) 的方式建立 Retrofit 實例，確保只在第一次使用時才被初始化
    private val retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create()) // 使用 Gson 作為 JSON 解析器
            .build()
    }

    // 對外提供一個獲取 ApiService 實例的方法
    val api: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }
}