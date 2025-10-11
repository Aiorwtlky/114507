package com.example.mdgapp

import android.app.Application
import com.example.mdgapp.data.local.TokenManager
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow

class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        // 保留你原有的 TokenManager 初始化
        TokenManager.initialize(this)
        // 設定一個靜態實例，方便從 App 的任何地方存取
        instance = this
    }

    // companion object 允許我們建立可以在 App 中共用的靜態成員
    companion object {
        // lateinit 表示我們會稍後（在 onCreate 中）初始化它
        lateinit var instance: MyApplication
            private set

        // 1. 建立一個私有的、可變的 SharedFlow，用於發送登出訊號
        private val _logoutEvent = MutableSharedFlow<Unit>()

        // 2. 對外提供一個公開的、唯讀的 SharedFlow，讓其他類別 (如 MainActivity) 監聽
        val logoutEvent = _logoutEvent.asSharedFlow()

        /**
         * 這是從 App 任何地方（主要是 AuthInterceptor）呼叫的函式，
         * 用於觸發全域登出事件。
         */
        suspend fun triggerLogout() {
            _logoutEvent.emit(Unit)
        }
    }
}