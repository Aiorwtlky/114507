package com.example.mdgapp.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController

data class Announcement(val date: String, val title: String, val preview: String)

@Composable
fun AnnouncementListScreen(navController: NavController?) {
    val announcements = listOf(
        Announcement("2025/07/28", "系統維護通知", "7/29 晚間將進行系統升級，屆時可能短暫無法使用..."),
        Announcement("2025/07/25", "新功能上線", "群組功能正式推出，歡迎駕駛們使用！"),
        Announcement("2025/07/20", "放假公告", "吾駕仙團隊將於月底放假兩日，如需客服請提前聯繫...")
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(16.dp)
    ) {
        Text("公告內容", color = Color.White, fontSize = 24.sp)

        Spacer(modifier = Modifier.height(12.dp))

        LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            items(announcements) { item ->
                AnnouncementCard(item) {
                    navController?.navigate("announcementDetail/${item.title}")
                }
            }
        }
    }
}

@Composable
fun AnnouncementCard(item: Announcement, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }, // ← 點擊回呼
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2B2B2B))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = item.date, color = Color.Gray, fontSize = 12.sp)
            Spacer(modifier = Modifier.height(4.dp))
            Text(text = item.title, color = Color.White, fontSize = 18.sp)
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = item.preview,
                color = Color.LightGray,
                fontSize = 14.sp,
                maxLines = 2
            )
        }
    }
}

