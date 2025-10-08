package com.example.mdgapp.ui.screen

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.mdgapp.R
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.navigation.NavController



data class ChatItem(
    val id: Int,
    val name: String,
    val message: String,
    val time: String,
    val unreadCount: Int,
    val avatarRes: Int
)

val chatList = listOf(
    ChatItem(1, "季博達", "讚!", "17:04", 1, R.drawable.jiboda1),
    ChatItem(2, "純愛戰神", "酷!", "7/26", 0, R.drawable.jiboda2),
    ChatItem(3, "haerin", "愛你呦寶寶<3", "7/26", 0, R.drawable.mywife),
)

@Composable
fun ChatListScreen(navController: NavController) {
    LazyColumn(modifier = Modifier.fillMaxSize().padding(8.dp)) {
        items(chatList) { chat ->
            ChatListItem(chat = chat) {
                navController.navigate("chatDetail/${chat.id}") // 不加 popUpTo
            }
        }
    }
}

@Composable
fun ChatListItem(chat: ChatItem, onClick: () -> Unit = {}) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() } // 點擊切換
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // 大頭貼
        Image(
            painter = painterResource(id = chat.avatarRes),
            contentDescription = "Avatar",
            modifier = Modifier
                .size(48.dp)
                .clip(CircleShape)
        )

        Spacer(modifier = Modifier.width(12.dp))

        // 中間：名字與訊息
        Column(modifier = Modifier.weight(1f)) {
            Text(chat.name, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Text(chat.message, fontSize = 14.sp, color = Color.Gray, maxLines = 1)
        }

        // 右側：時間與未讀數
        Column(horizontalAlignment = Alignment.End) {
            Text(chat.time, fontSize = 12.sp, color = Color.Gray)

            if (chat.unreadCount > 0) {
                Box(
                    modifier = Modifier
                        .padding(top = 4.dp)
                        .size(20.dp)
                        .clip(CircleShape)
                        .background(Color.Red),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = chat.unreadCount.toString(),
                        fontSize = 12.sp,
                        color = Color.White
                    )
                }
            }
        }
    }
}
