@file:OptIn(ExperimentalMaterial3Api::class)
package com.example.mdgapp.ui.screen

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.*
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.model.ChatMessage
import com.example.mdgapp.model.ChatItem

@Composable
fun ChatDetailScreen(chat: ChatItem, navController: NavController) {
    val allMessages = mapOf(
        1 to listOf(
            ChatMessage(1, "我", imageRes = R.drawable.jiboda1, timestamp = "22:12", text = ""),
            ChatMessage(2, "季博達", imageRes = R.drawable.jiboda2, timestamp = "22:15", text = ""),
            ChatMessage(3, "季博達", imageRes = null, timestamp = "22:10", text = "讚!"),
        ),
        2 to listOf(
            ChatMessage(1, "純愛戰神", R.drawable.mdg_logo, "20:01")
        ),
        3 to listOf(
            ChatMessage(1, "haerin", imageRes = null, "01:30", text = "愛你呦寶寶")
        )
    )

    val messages = remember {
        mutableStateListOf<ChatMessage>().apply {
            addAll(allMessages[chat.id] ?: emptyList())
        }
    }

    var inputText by remember { mutableStateOf(TextFieldValue("")) }
    val focusManager = LocalFocusManager.current

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text(chat.name, color = Color.White, fontSize = 18.sp) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color(0xFF1C1C1C)
                ),
                modifier = Modifier.height(48.dp)
            )
        },
        containerColor = Color.Black
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                contentPadding = PaddingValues(top = 8.dp, bottom = 12.dp)
            ) {
                items(messages) { msg ->
                    MessageBubble(msg)
                }
            }

            ChatInputField(
                value = inputText,
                onInputChange = { inputText = it },
                onSend = {
                    if (inputText.text.isNotBlank()) {
                        messages.add(
                            ChatMessage(
                                id = messages.size + 1,
                                sender = "自己",
                                imageRes = null,
                                timestamp = "00:05",
                                text = inputText.text
                            )
                        )
                        inputText = TextFieldValue("")
                        focusManager.clearFocus()
                    }
                }
            )
        }
    }
}

@Composable
fun MessageBubble(message: ChatMessage) {
    val isMine = message.sender == "我" || message.sender == "自己"

    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = if (isMine) Alignment.End else Alignment.Start
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 260.dp)
                .background(
                    color = if (isMine) Color(0xFF1C1C1E) else Color(0xFF2A2A2E),
                    shape = RoundedCornerShape(12.dp)
                )
                .padding(8.dp)
        ) {
            if (message.text.isNotBlank()) {
                Text(
                    text = message.text,
                    color = Color.White,
                    fontSize = 14.sp
                )
            }

            message.imageRes?.let {
                Spacer(modifier = Modifier.height(6.dp))
                Image(
                    painter = painterResource(id = it),
                    contentDescription = "Image message",
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .fillMaxWidth()
                        .heightIn(min = 100.dp)
                )
            }
        }

        Text(
            text = message.timestamp,
            fontSize = 12.sp,
            color = Color.Gray,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
        )
    }
}

@Composable
fun ChatInputField(
    value: TextFieldValue,
    onInputChange: (TextFieldValue) -> Unit,
    onSend: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.Black)
            .imePadding() // 避免被鍵盤擋住
            .padding(horizontal = 8.dp, vertical = 12.dp),
        verticalAlignment = Alignment.Bottom
    ) {
        TextField(
            value = value,
            onValueChange = onInputChange,
            placeholder = { Text("輸入訊息", color = Color.Gray) },
            textStyle = LocalTextStyle.current.copy(color = Color.LightGray, fontSize = 14.sp),
            modifier = Modifier
                .weight(1f)
                .heightIn(min = 48.dp),
            colors = TextFieldDefaults.colors(
                focusedContainerColor = Color(0xFF2A2A2E),
                unfocusedContainerColor = Color(0xFF2A2A2E),
                focusedTextColor = Color.LightGray,
                unfocusedTextColor = Color.LightGray,
                disabledTextColor = Color.Gray,
                focusedIndicatorColor = Color.Transparent,
                unfocusedIndicatorColor = Color.Transparent
            )
        )

        Spacer(modifier = Modifier.width(8.dp))

        IconButton(onClick = onSend) {
            Icon(
                painter = painterResource(R.drawable.mdg_logo),
                contentDescription = "Send",
                tint = Color.Gray
            )
        }
    }
}
