// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/LaunchScreen.kt

package com.example.mdgapp.ui.screen

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import androidx.navigation.compose.rememberNavController
import com.example.mdgapp.R
import com.example.mdgapp.data.local.TokenManager // 👈 【重點】1. 匯入 TokenManager
import com.example.mdgapp.ui.theme.MyApplicationTheme
import kotlinx.coroutines.delay

@Composable
fun LaunchScreen(
    navController: NavController,
    previewMode: Boolean = false
) {
    var visible by remember { mutableStateOf(false) }

    // 在非預覽模式下，才執行我們的檢查與導航邏輯
    if (!previewMode) {
        // LaunchedEffect 會在畫面第一次顯示時執行一次
        LaunchedEffect(key1 = true) {
            visible = true
            delay(2000) // 讓 Logo 動畫有時間播放

            // ▼▼▼▼▼ 【重點】2. 核心決策邏輯 ▼▼▼▼▼
            // 從 TokenManager 檢查本機是否有 Token
            val token = TokenManager.getToken()

            // 決定下一個畫面的路徑
            val destination = if (token.isNullOrBlank()) {
                // 如果沒有 Token，目標是登入頁
                "login"
            } else {
                // 如果有 Token，目標是主頁
                "home"
            }

            // 執行導航
            navController.navigate(destination) {
                // 從返回堆疊中移除 launch 畫面，讓使用者按返回鍵時不會再回到這裡
                popUpTo("launch") { inclusive = true }
            }
            // ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
        }
    } else {
        // 在預覽模式下，僅顯示動畫，不進行導航
        LaunchedEffect(Unit) {
            visible = true
        }
    }

    // --- 以下的 UI 程式碼完全保持不變 ---
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(animationSpec = tween(durationMillis = 1500))
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Surface(
                    shape = RoundedCornerShape(36.dp),
                    shadowElevation = 12.dp,
                    color = Color(0xFFF8FAF5)
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.mdg_logo),
                        contentDescription = "MDG Logo",
                        contentScale = ContentScale.Crop,
                        modifier = Modifier.size(200.dp)
                    )
                }
            }
        }
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF000000)
@Composable
fun PreviewLaunchScreen() {
    MyApplicationTheme(darkTheme = true) {
        LaunchScreen(navController = rememberNavController(), previewMode = true)
    }
}