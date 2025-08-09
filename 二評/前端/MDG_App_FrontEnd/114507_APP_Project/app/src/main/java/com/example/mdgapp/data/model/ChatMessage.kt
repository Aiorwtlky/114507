package com.example.mdgapp.model

data class ChatMessage(
    val id: Int,
    val sender: String,
    val imageRes: Int? = null, // ✅ 可為 null，表示不顯示圖片
    val timestamp: String,
    val text: String = ""
)

