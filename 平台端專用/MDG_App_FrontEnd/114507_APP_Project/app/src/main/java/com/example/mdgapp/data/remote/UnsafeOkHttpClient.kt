package com.example.mdgapp.data.remote

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.security.SecureRandom
import java.security.cert.X509Certificate
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

/**
 * 取得一個信任所有憑證的 OkHttpClient.Builder。
 * 警告：這會繞過 SSL 憑證驗證，僅限開發和測試使用。
 */
fun getUnsafeOkHttpClientBuilder(): OkHttpClient.Builder {
    try {
        // 建立一個信任所有憑證的 TrustManager
        val trustAllCerts = arrayOf<TrustManager>(
            object : X509TrustManager {
                override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
                override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {}
                override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
            }
        )

        // 安裝這個 TrustManager
        val sslContext = SSLContext.getInstance("SSL")
        sslContext.init(null, trustAllCerts, SecureRandom())

        // 建立一個使用該 TrustManager 的 SSLSocketFactory
        val sslSocketFactory = sslContext.socketFactory

        val builder = OkHttpClient.Builder()
        builder.sslSocketFactory(sslSocketFactory, trustAllCerts[0] as X509TrustManager)
        builder.hostnameVerifier { _, _ -> true } // 信任所有主機名稱

        return builder
    } catch (e: Exception) {
        throw RuntimeException(e)
    }
}