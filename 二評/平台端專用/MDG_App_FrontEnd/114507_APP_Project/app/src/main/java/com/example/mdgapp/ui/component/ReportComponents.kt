package com.example.mdgapp.ui.component

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.mdgapp.data.model.DangerousEventItem
import com.example.mdgapp.data.model.PerformanceMetrics
import com.example.mdgapp.data.model.TripInfo
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.TextStyle
import java.util.Locale

// --- ✅ 新增：根據分數回傳對應顏色的輔助函式 ---
@Composable
private fun getScoreColor(score: Int): Color {
    return when {
        score >= 90 -> Color(0xFF87CEEB) // 淡藍色 (Sky Blue)
        score >= 80 -> Color.Green
        score >= 60 -> Color.Yellow
        else -> Color.Red
    }
}

@Composable
fun ReportListItemCard(date: LocalDate, totalScore: Int, onClick: () -> Unit) {
    val dayOfWeek = date.dayOfWeek.getDisplayName(TextStyle.FULL, Locale.TRADITIONAL_CHINESE)
    val formattedDate = date.format(DateTimeFormatter.ofPattern("yyyy / MM / dd"))

    Card(
        onClick = onClick,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(formattedDate, color = Color.White, fontSize = 18.sp)
                // --- ✅ 修改點：讓分數顯示對應顏色 ---
                Row {
                    Text("$dayOfWeek - 總分: ", color = Color.Gray, fontSize = 14.sp)
                    Text(
                        text = totalScore.toString(),
                        color = getScoreColor(score = totalScore),
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                }
            }
            Icon(
                imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                contentDescription = "查看報表",
                tint = Color.White
            )
        }
    }
}

@Composable
fun ScoreHeader(score: Int, rating: String, feedback: String) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("本次駕駛總分", fontSize = 16.sp, color = Color.Gray)
            Text(score.toString(), fontSize = 64.sp, fontWeight = FontWeight.Bold, color = Color.White)
            // --- ✅ 修改點：讓評級文字顯示對應顏色 ---
            Text(
                text = rating,
                fontSize = 20.sp,
                color = getScoreColor(score = score)
            )
            Spacer(modifier = Modifier.height(12.dp))
            HorizontalDivider(color = Color.Gray)
            Spacer(modifier = Modifier.height(12.dp))
            Text("AI 智慧評語", fontSize = 14.sp, color = Color.Gray)
            Text(feedback, fontSize = 16.sp, color = Color.White, modifier = Modifier.padding(top = 4.dp))
        }
    }
}

// ... 以下其他元件保持不變 ...

@Composable
fun MetricsCard(metrics: PerformanceMetrics) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("分項表現", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Spacer(modifier = Modifier.height(12.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                MetricItem("安全駕駛", metrics.safety)
                MetricItem("駕駛行為", metrics.behavior)
                MetricItem("法規遵守", metrics.compliance)
                MetricItem("行車效率", metrics.efficiency)
            }
        }
    }
}

@Composable
fun MetricItem(label: String, score: Int) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(score.toString(), fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.White)
        Text(label, fontSize = 12.sp, color = Color.Gray)
    }
}

@Composable
fun EventLogCard(events: List<DangerousEventItem>) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("事件紀錄與改善建議", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Spacer(modifier = Modifier.height(12.dp))
            events.forEach { event ->
                EventRow(event)
                HorizontalDivider(color = Color(0xFF424242), modifier = Modifier.padding(vertical = 8.dp))
            }
        }
    }
}

@Composable
fun EventRow(event: DangerousEventItem) {
    Column(Modifier.fillMaxWidth()) {
        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Text(event.eventType, color = Color.White, fontWeight = FontWeight.Bold)
            Text("-${event.deductionPoints}分", color = Color.Red, fontWeight = FontWeight.Bold)
        }
        Text("${event.time} | 嚴重程度: ${event.severity}", color = Color.Gray, fontSize = 12.sp)
        Spacer(modifier = Modifier.height(4.dp))
        Text("改善建議: ${event.suggestion}", color = Color.LightGray, fontSize = 14.sp)
    }
}

@Composable
fun TripInfoCard(info: TripInfo) {
    // 實作行程資訊卡...
}
