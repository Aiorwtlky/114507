package com.example.mdgapp.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnnouncementDetailScreen(title: String, navController: NavController? = null) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("公告內容", color = Color.White) },
                navigationIcon = {
                    IconButton(onClick = { navController?.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.Black)
            )
        },
        containerColor = Color.Black
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .fillMaxSize()
                .padding(16.dp)
        ) {
            Text(title, fontSize = 22.sp, color = Color.White)
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "這裡是「$title」的詳細公告內容。\n可根據公告 ID 或標題載入完整內文。",
                fontSize = 16.sp,
                color = Color.LightGray
            )
        }
    }
}

