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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.mdgapp.R
import com.example.mdgapp.ui.theme.MyApplicationTheme
import kotlinx.coroutines.delay

@Composable
fun LaunchScreen(
    // 參數現在只有 onTimeout 回呼函式
    onTimeout: () -> Unit,
    previewMode: Boolean = false
) {
    var visible by remember { mutableStateOf(false) }

    // 在非預覽模式下，執行計時並呼叫回呼
    if (!previewMode) {
        LaunchedEffect(Unit) {
            visible = true
            delay(2500)
            onTimeout() // 計時結束，通知 MainActivity
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
                        modifier = Modifier
                            .size(200.dp)
                            .clip(RoundedCornerShape(36.dp))
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
        LaunchScreen(onTimeout = {}, previewMode = true)
    }
}
