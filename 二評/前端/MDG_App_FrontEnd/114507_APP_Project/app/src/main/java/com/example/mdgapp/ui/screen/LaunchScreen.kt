package com.example.mdgapp.ui.screen

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.ui.theme.MyApplicationTheme
import kotlinx.coroutines.delay

@Composable
fun LaunchScreen(navController: NavController? = null, previewMode: Boolean = false) {
    var visible by remember { mutableStateOf(previewMode) }

    LaunchedEffect(Unit) {
        if (!previewMode) {
            visible = true
            delay(2000)
            navController?.navigate("register") {
                popUpTo("launch") { inclusive = true }
            }
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
            enter = fadeIn()
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
        LaunchScreen(previewMode = true)
    }
}

