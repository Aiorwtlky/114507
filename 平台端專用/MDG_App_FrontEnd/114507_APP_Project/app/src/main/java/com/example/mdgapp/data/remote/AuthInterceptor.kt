package com.example.mdgapp.data.remote

import com.example.mdgapp.data.local.TokenManager
import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        // 從 TokenManager 取得儲存的 token
        val token = TokenManager.getToken()
        val requestBuilder = chain.request().newBuilder()

        // 如果 token 存在，就將它加入到請求的 Header 中
        token?.let {
            requestBuilder.addHeader("Authorization", "Bearer $it")
        }

        return chain.proceed(requestBuilder.build())
    }
}