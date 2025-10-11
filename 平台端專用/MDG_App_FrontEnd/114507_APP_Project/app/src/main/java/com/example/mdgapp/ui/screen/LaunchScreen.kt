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
import com.example.mdgapp.data.local.TokenManager
import com.example.mdgapp.ui.theme.MyApplicationTheme
import com.example.mdgapp.ui.theme.iOsBackground
import com.example.mdgapp.ui.theme.iOsBlue // ✅ 匯入藍色
import kotlinx.coroutines.delay

@Composable
fun LaunchScreen(
    navController: NavController,
    previewMode: Boolean = false
) {
    var visible by remember { mutableStateOf(false) }

    if (!previewMode) {
        LaunchedEffect(key1 = true) {
            visible = true
            delay(2000)

            val token = TokenManager.getToken()
            val destination = if (token.isNullOrBlank()) "login" else "home"

            navController.navigate(destination) {
                popUpTo("launch") { inclusive = true }
            }
        }
    } else {
        LaunchedEffect(Unit) {
            visible = true
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(iOsBackground), // ✅ 背景顏色改為藍色
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

@Preview(showBackground = true)
@Composable
fun PreviewLaunchScreen() {
    MyApplicationTheme(darkTheme = true) {
        // ✅ 預覽也使用藍色背景
        Box(Modifier.background(iOsBackground)) {
            LaunchScreen(navController = rememberNavController(), previewMode = true)
        }
    }
}