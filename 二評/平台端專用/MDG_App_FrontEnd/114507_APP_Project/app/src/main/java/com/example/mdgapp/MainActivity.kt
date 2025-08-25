package com.example.mdgapp

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.Color
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.navigation.compose.rememberNavController
import com.example.mdgapp.navigation.AppNavGraph
import com.example.mdgapp.ui.screen.LaunchScreen
import com.example.mdgapp.ui.theme.MyApplicationTheme
import com.google.accompanist.systemuicontroller.rememberSystemUiController

class MainActivity : ComponentActivity() {

    private val CAMERA_PERMISSION_REQUEST = 1001

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 您的相機權限請求邏輯 (保持不變)
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.CAMERA),
                CAMERA_PERMISSION_REQUEST
            )
        }

        setContent {
            MyApplicationTheme(darkTheme = true) {
                // 您的狀態列顏色設定 (保持不變)
                SetStatusBarBlack()

                // --- 整合新的啟動流程 ---
                var showSplashScreen by remember { mutableStateOf(true) }

                if (showSplashScreen) {
                    // 顯示啟動畫面，並在計時結束後更新狀態
                    LaunchScreen(onTimeout = { showSplashScreen = false })
                } else {
                    // 啟動畫面結束後，才顯示主程式的導航
                    val navController = rememberNavController()
                    AppNavGraph(navController)
                }
            }
        }
    }
}

@Composable
fun SetStatusBarBlack() {
    val systemUiController = rememberSystemUiController()
    SideEffect {
        systemUiController.setStatusBarColor(
            color = Color.Black,
            darkIcons = false // 白字
        )
    }
}
