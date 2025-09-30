// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/ReportDetailScreen.kt

package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.mdgapp.data.model.TripDetail
import com.example.mdgapp.ui.component.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportDetailScreen(
    navController: NavController,
    tripId: Int?,
    // ▼▼▼ 【核心修改】讓此畫面直接接收「資料」和「動作」，而不是特定的 ViewModel ▼▼▼
    report: TripDetail?,
    onFetchDetails: (Int) -> Unit
) {
    // 當 tripId 存在且發生變化時，執行 onFetchDetails 這個動作
    LaunchedEffect(tripId) {
        tripId?.let(onFetchDetails)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("駕駛行為報表") },
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
        bottomBar = {
            Surface(color = Color.Black) {
                DownloadReportButton(modifier = Modifier.padding(16.dp))
            }
        },
        containerColor = Color.Black
    ) { paddingValues ->
        // 如果 report 物件不為 null，則顯示內容
        report?.let { detailedReport ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(horizontal = 16.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Spacer(modifier = Modifier.height(0.dp))

                val score = detailedReport.score.toDoubleOrNull()?.toInt() ?: 0
                val scoreRating = when {
                    score >= 90 -> "優秀"
                    score >= 80 -> "良好"
                    score >= 60 -> "警告"
                    else -> "危險"
                }

                ScoreHeader(
                    totalScore = score,
                    scoreRating = scoreRating,
                    geminiFeedback = detailedReport.aiSuggestion
                )

                EventLogCard(events = detailedReport.aiVisionLogSet)
                Spacer(modifier = Modifier.height(16.dp))
            }
        } ?: Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            // 如果 report 物件為 null (正在載入)，則顯示讀取動畫
            CircularProgressIndicator()
        }
    }
}