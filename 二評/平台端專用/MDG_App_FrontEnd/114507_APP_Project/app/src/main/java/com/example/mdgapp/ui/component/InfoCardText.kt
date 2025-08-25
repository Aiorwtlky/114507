package com.example.mdgapp.ui.component

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.draw.clip

@Composable
fun InfoCardText(
    valueText: String,
    label: String,
    fillColor: Color,
    backgroundColor: Color,
    progressValue: Float,         // ✅ 真實值
    maxProgress: Float,           // ✅ 最大值
    modifier: Modifier = Modifier
) {
    val progress = (progressValue / maxProgress).coerceIn(0f, 1f)

    Card(
        modifier = modifier.height(100.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        elevation = CardDefaults.cardElevation(4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text(valueText, color = Color.White, fontSize = 20.sp)
            Text(label, color = Color.Gray, fontSize = 12.sp)
            LinearProgressIndicator(
                progress = progress,
                color = fillColor,
                trackColor = backgroundColor,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .clip(RoundedCornerShape(4.dp))
            )
        }
    }
}
