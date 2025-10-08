// 檔案路徑: app/src/main/java/com/example/mdgapp/data/local/TokenManager.kt

package com.example.mdgapp.data.local

import android.content.Context
import android.content.SharedPreferences

object TokenManager {

    private const val PREFS_NAME = "MyAppPrefs"
    private const val KEY_AUTH_TOKEN = "auth_token"
    private lateinit var prefs: SharedPreferences

    fun initialize(context: Context) {
        prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    fun saveToken(token: String) {
        prefs.edit().putString(KEY_AUTH_TOKEN, token).apply()
    }

    fun getToken(): String? {
        return prefs.getString(KEY_AUTH_TOKEN, null)
    }

    fun clearToken() {
        prefs.edit().remove(KEY_AUTH_TOKEN).apply()
    }
}