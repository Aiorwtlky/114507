// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/component/ReportComponents.kt

package com.example.mdgapp.ui.component

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
import com.example.mdgapp.data.model.AiVisionLog
import com.example.mdgapp.data.model.PerformanceMetrics
import com.example.mdgapp.data.model.TripInfo
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.TextStyle
import java.util.Locale

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

// ▼▼▼ 【修改重點 1】修改 ScoreHeader 的參數名稱 ▼▼▼
@Composable
fun ScoreHeader(
    totalScore: Int,
    scoreRating: String,
    geminiFeedback: String
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("本次駕駛總分", fontSize = 16.sp, color = Color.Gray)
            // 使用新的參數名稱
            Text(totalScore.toString(), fontSize = 64.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Text(
                text = scoreRating,
                fontSize = 20.sp,
                color = getScoreColor(score = totalScore)
            )
            Spacer(modifier = Modifier.height(12.dp))
            HorizontalDivider(color = Color.Gray)
            Spacer(modifier = Modifier.height(12.dp))
            Text("AI 智慧評語", fontSize = 14.sp, color = Color.Gray)
            // 使用新的參數名稱
            Text(geminiFeedback, fontSize = 16.sp, color = Color.White, modifier = Modifier.padding(top = 4.dp))
        }
    }
}

// ▼▼▼ 【修改重點 2】修改 EventLogCard 和 EventRow 來接收新的資料模型 ▼▼▼
@Composable
fun EventLogCard(events: List<AiVisionLog>) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("事件紀錄與改善建議", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Spacer(modifier = Modifier.height(12.dp))
            // 如果沒有事件，顯示提示訊息
            if (events.isEmpty()) {
                Text("本次行程無特別事件紀錄。", color = Color.Gray, fontSize = 14.sp)
            } else {
                events.forEach { event ->
                    EventRow(event) // 將 AiVisionLog 物件傳遞給 EventRow
                    HorizontalDivider(color = Color(0xFF424242), modifier = Modifier.padding(vertical = 8.dp))
                }
            }
        }
    }
}

@Composable
fun EventRow(event: AiVisionLog) {
    Column(Modifier.fillMaxWidth()) {
        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            // 使用 AiVisionLog 和其巢狀的 AiEvent 物件中的資料
            Text(event.event.description, color = Color.White, fontWeight = FontWeight.Bold)
            Text("-${event.event.deductionPoints}分", color = Color.Red, fontWeight = FontWeight.Bold)
        }
        Text(event.timestamp, color = Color.Gray, fontSize = 12.sp)
        Spacer(modifier = Modifier.height(4.dp))
        // API 文件中沒有提供改善建議，我們先顯示事件詳情
        Text("詳細資訊: ${event.eventDetails}", color = Color.LightGray, fontSize = 14.sp)
    }
}


// --- 以下元件保持不變 ---

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
fun TripInfoCard(info: TripInfo) {
    // 實作行程資訊卡...
}