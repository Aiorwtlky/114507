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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.mdgapp.data.model.VideoFile
import com.example.mdgapp.data.viewmodel.DownloadViewModel
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.TextStyle
import java.util.Locale

// 新的、用於日期列表的卡片
@Composable
fun DateListItemCard(date: LocalDate, videoCount: Int, onClick: () -> Unit) {
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
                Text("$dayOfWeek - 共 $videoCount 個影像檔", color = Color.Gray, fontSize = 14.sp)
            }
            Icon(
                imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                contentDescription = "查看詳情",
                tint = Color.White
            )
        }
    }
}

@Composable
fun TimeSlotHeader(timeSlotIndex: Int) {
    val startTime = timeSlotIndex * 3
    val endTime = startTime + 3
    val timeRange = String.format("%02d:00 - %02d:00", startTime, endTime)

    Text(
        text = timeRange,
        color = Color.LightGray,
        fontWeight = FontWeight.Bold,
        modifier = Modifier.padding(vertical = 8.dp)
    )
}

@Composable
fun VideoFileCard(videoFile: VideoFile) {
    val context = LocalContext.current
    val viewModel: DownloadViewModel = viewModel()
    val formattedTime = videoFile.timestamp.format(DateTimeFormatter.ofPattern("HH:mm:ss"))
    val fileSizeMB = "%.1f MB".format(videoFile.fileSize / 1_000_000.0)

    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(videoFile.fileName, color = Color.White, fontSize = 14.sp)
            Text("$formattedTime - $fileSizeMB", color = Color.Gray, fontSize = 12.sp)
        }
        Button(
            onClick = { viewModel.startDownload(context, videoFile) },
            colors = ButtonDefaults.buttonColors(containerColor = Color.Gray, contentColor = Color.White),
            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp)
        ) {
            Text("下載")
        }
    }
}
