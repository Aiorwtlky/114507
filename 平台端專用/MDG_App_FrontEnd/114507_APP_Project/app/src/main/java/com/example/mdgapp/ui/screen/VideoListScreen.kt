package com.example.mdgapp.ui.screen

import android.widget.Toast
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.PlayCircle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.data.model.VideoFile
import com.example.mdgapp.data.viewmodel.DriverDownloadViewModel
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VideoListScreen(
    navController: NavController,
    dateString: String?,
    // ✅ 步驟二：接收 ManagerDownloadViewModel
    viewModel: DriverDownloadViewModel = viewModel()
) {
    // 解析從導航傳來的日期字串
    val selectedDate = remember(dateString) {
        dateString?.let { LocalDate.parse(it) }
    }

    // ✅ 當 selectedDate 發生變化時 (即進入此畫面時)，通知 ViewModel 更新其狀態
    LaunchedEffect(selectedDate) {
        selectedDate?.let {
            viewModel.selectDate(it)
        }
    }

    // ✅ 從 ViewModel 收集特定日期的影片紀錄
    val selectedLog by viewModel.selectedDateLog.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    val formattedDate = selectedDate?.format(DateTimeFormatter.ofPattern("yyyy / MM / dd")) ?: "載入中..."
                    Text(formattedDate)
                },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(imageVector = Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Black,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        },
        containerColor = Color.Black
    ) { paddingValues ->
        // 根據 selectedLog 的狀態決定顯示內容
        if (selectedLog == null) {
            Box(modifier = Modifier.fillMaxSize().padding(paddingValues), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Color.White)
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(paddingValues),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // ✅ 使用從 ViewModel 來的真實影片數據
                items(selectedLog!!.videos, key = { it.id }) { video ->
                    VideoListItem(videoFile = video)
                }
            }
        }
    }
}

@Composable
fun VideoListItem(videoFile: VideoFile) {
    val context = LocalContext.current
    val timeFormatter = remember { DateTimeFormatter.ofPattern("HH:mm:ss") }

    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth().clickable {
            Toast.makeText(context, "播放 ${videoFile.fileName}", Toast.LENGTH_SHORT).show()
        }
    ) {
        Row(
            modifier = Modifier.height(IntrinsicSize.Min),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(modifier = Modifier.size(120.dp), contentAlignment = Alignment.Center) {
                Image(
                    painter = painterResource(id = R.drawable.fake_map), // 示意圖
                    contentDescription = "影片縮圖",
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxSize()
                )
                Icon(
                    imageVector = Icons.Default.PlayCircle,
                    contentDescription = "播放",
                    tint = Color.White.copy(alpha = 0.8f),
                    modifier = Modifier.size(48.dp)
                )
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.padding(vertical = 8.dp)) {
                Text(
                    "開始時間: ${videoFile.timestamp.format(timeFormatter)}",
                    color = Color.White,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    "檔案大小: ${String.format(Locale.US, "%.2f", videoFile.fileSize / 1_000_000_000.0)} GB",
                    color = Color.Gray,
                    fontSize = 14.sp
                )
            }
        }
    }
}