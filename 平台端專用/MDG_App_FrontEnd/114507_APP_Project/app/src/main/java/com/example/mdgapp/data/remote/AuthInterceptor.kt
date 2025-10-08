// 檔案路徑: app/src/main/java/com/example/mdgapp/data/remote/AuthInterceptor.kt

package com.example.mdgapp.data.remote

import com.example.mdgapp.data.local.TokenManager
import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        // 取得原始的 request
        val originalRequest = chain.request()

        // 從 TokenManager 獲取已儲存的 Token
        val token = TokenManager.getToken()

        // 如果 Token 存在，就建立一個新的 request 並附加上 Authorization Header
        val newRequest = if (token != null) {
            originalRequest.newBuilder()
                .header("Authorization", "Token $token")
                .build()
        } else {
            // 如果沒有 Token (例如登入、註冊時)，就使用原始的 request
            originalRequest
        }

        // 讓請求繼續進行
        return chain.proceed(newRequest)
    }
}