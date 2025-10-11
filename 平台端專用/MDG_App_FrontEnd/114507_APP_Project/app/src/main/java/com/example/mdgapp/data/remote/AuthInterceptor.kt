package com.example.mdgapp.data.remote

import com.example.mdgapp.MyApplication
import com.example.mdgapp.data.local.TokenManager
import kotlinx.coroutines.runBlocking
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

        val request = requestBuilder.build()
        val response = chain.proceed(request)

        // 檢查 HTTP 狀態碼是否為 401 (Unauthorized)
        if (response.code == 401) {
            // 如果是 401，表示 token 失效或未授權
            // 使用 runBlocking 是因為 intercept 是同步函式，而我們的 triggerLogout 是 suspend 函式
            runBlocking {
                // 清除本地儲存的 token
                TokenManager.clearToken()
                // 觸發全域的登出事件
                MyApplication.triggerLogout()
            }
        }

        return response
    }
}