package com.example.mdgapp.ui.component

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.mdgapp.data.model.DangerousEventItem
import java.time.LocalDate
import java.time.format.DateTimeFormatter

@Composable
fun ScoreHeader(score: Int, rating: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E))
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text("綜合總分", color = Color.Gray)
            Text(
                text = score.toString(),
                fontSize = 48.sp,
                fontWeight = FontWeight.Bold,
                color = when (rating) {
                    "優秀" -> Color.Green
                    "良好" -> Color.Cyan
                    "警告" -> Color.Yellow
                    else -> Color.Red
                }
            )
            Text(rating, fontSize = 20.sp, color = Color.White)
        }
    }
}

@Composable
fun GeminiFeedbackCard(feedback: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Info,
                contentDescription = "AI 建議",
                tint = Color.Cyan
            )
            Text(
                text = feedback,
                fontSize = 14.sp,
                color = Color.LightGray
            )
        }
    }
}

@Composable
fun EventLogCard(events: List<DangerousEventItem>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("危險事件紀錄", style = MaterialTheme.typography.titleLarge, color = Color.White)
            Spacer(modifier = Modifier.height(8.dp))

            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                if (events.isEmpty()) {
                    Text("本次行程沒有偵測到危險事件。", color = Color.Gray, modifier = Modifier.padding(vertical = 8.dp))
                } else {
                    events.forEachIndexed { index, event ->
                        Column {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(event.eventType, fontWeight = FontWeight.Bold, color = Color.White)
                                Text(event.time, color = Color.Gray, fontSize = 14.sp)
                            }
                            Spacer(modifier = Modifier.height(4.dp))
                            Text("風險等級: ${event.severity} (扣 ${event.deductionPoints} 分)", color = Color.LightGray, fontSize = 14.sp)
                            Spacer(modifier = Modifier.height(4.dp))
                            Text("AI 建議: ${event.suggestion}", color = Color.LightGray, fontSize = 14.sp)
                        }
                        if (index < events.lastIndex) {
                            HorizontalDivider(color = Color(0xFF424242), thickness = 0.5.dp, modifier = Modifier.padding(top = 16.dp))
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ReportListItemCard(
    date: LocalDate,
    totalScore: Int,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(date.format(DateTimeFormatter.ofPattern("yyyy-MM-dd")), color = Color.White, fontSize = 16.sp)
            Text("總分: $totalScore", color = Color.White, fontSize = 16.sp)
        }
    }
}