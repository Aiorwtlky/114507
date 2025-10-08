// 檔案路徑: app/src/main/java/com/example/mdgapp/MyApplication.kt

package com.example.mdgapp

import android.app.Application
import com.example.mdgapp.data.local.TokenManager

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // 在 App 啟動時初始化 TokenManager
        TokenManager.initialize(this)
    }
}