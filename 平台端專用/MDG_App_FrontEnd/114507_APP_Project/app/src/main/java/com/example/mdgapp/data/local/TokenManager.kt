package com.example.mdgapp.data.local

import android.content.Context
import android.content.SharedPreferences

object TokenManager {

    private const val PREFS_NAME = "app_prefs"
    private const val USER_TOKEN_KEY = "user_token"

    private lateinit var sharedPreferences: SharedPreferences

    /**
     * 這個方法必須在 MyApplication 的 onCreate 中被呼叫一次，
     * 用來初始化 SharedPreferences。
     */
    fun initialize(context: Context) {
        sharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    /**
     * 儲存 Token
     */
    fun saveToken(token: String) {
        sharedPreferences.edit().putString(USER_TOKEN_KEY, token).apply()
    }

    /**
     * 讀取 Token
     */
    fun getToken(): String? {
        return sharedPreferences.getString(USER_TOKEN_KEY, null)
    }

    /**
     * 清除 Token
     */
    fun clearToken() {
        sharedPreferences.edit().remove(USER_TOKEN_KEY).apply()
    }
}