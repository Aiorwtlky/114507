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
import com.example.mdgapp.ui.theme.MyApplicationTheme
import kotlinx.coroutines.delay

@Composable
fun LaunchScreen(
    // ✅ 修正 1：參數改為接收 NavController
    navController: NavController,
    previewMode: Boolean = false
) {
    var visible by remember { mutableStateOf(false) }

    // 在非預覽模式下，執行計時並導航
    if (!previewMode) {
        LaunchedEffect(Unit) {
            visible = true
            delay(2500) // 啟動畫面顯示時長
            // ✅ 修正 1：計時結束，直接使用 navController 導航
            navController.navigate("register") {
                // 從返回堆疊中移除啟動畫面，避免使用者按返回鍵回到這裡
                popUpTo("launch") { inclusive = true }
            }
        }
    } else {
        // 在預覽模式下，僅顯示動畫
        LaunchedEffect(Unit) {
            visible = true
        }
    }

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
                        // ✅ 優化 1：移除了多餘的 clip
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
        // ✅ 修正 1：預覽時傳入一個假的 NavController
        LaunchScreen(navController = rememberNavController(), previewMode = true)
    }
}