package com.example.mdgapp.ui.screen

import android.graphics.Paint
import android.graphics.RectF
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.DriverHistoryViewModel
import com.example.mdgapp.ui.component.HistorySection
import kotlin.math.cos
import kotlin.math.sin

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DriverHistoryScreen(
    navController: NavController,
    viewModel: DriverHistoryViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("個人歷史數據總覽") },
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
        if (uiState.isLoading) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(16.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {
                // 核心數據卡片 (保持不變)
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    MetricCard("總累積里程", uiState.totalMileage.toString(), "公里", Modifier.weight(1f))
                    MetricCard("總駕駛時長", uiState.totalDurationHours.toString(), "小時", Modifier.weight(1f))
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    MetricCard("總行程次數", uiState.totalTrips.toString(), "次", Modifier.weight(1f))
                    MetricCard("生涯平均分數", uiState.lifetimeAverageScore.toString(), "分", Modifier.weight(1f))
                }

                // ✅ 1. 將「分數趨勢分析」替換為「主要違規分佈」
                HistorySection(title = "主要違規分佈") {
                    if (uiState.topEvents.isEmpty()) {
                        Text("無違規紀錄", color = Color.Green, modifier = Modifier.padding(16.dp))
                    } else {
                        PieChart(
                            data = uiState.topEvents,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(220.dp)
                                .padding(top = 8.dp)
                        )
                    }
                }

                // 駕駛行為分析 (保持不變)
                HistorySection(title = "駕駛行為分析") {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("總違規次數", color = Color.Gray, fontSize = 16.sp)
                            Text("${uiState.totalEvents} 次", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                        }
                        HorizontalDivider(color = Color(0xFF424242), modifier = Modifier.padding(vertical = 8.dp))

                        uiState.topEvents.forEach { (event, count) ->
                            EventStatRow(event, count)
                        }
                    }
                }
            }
        }
    }
}


// ... MetricCard 和 EventStatRow 保持不變 ...
@Composable
fun MetricCard(title: String, value: String, unit: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(title, color = Color.Gray, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.Bottom) {
                Text(value, color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.width(4.dp))
                Text(unit, color = Color.White, fontSize = 16.sp, modifier = Modifier.padding(bottom = 4.dp))
            }
        }
    }
}

@Composable
fun EventStatRow(event: String, count: Int) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(event, color = Color.White, fontSize = 16.sp)
        Text("$count 次", color = Color.Red, fontSize = 16.sp, fontWeight = FontWeight.Bold)
    }
}

// ✅ 2. 新增一個 PieChart Composable 函式
@Composable
fun PieChart(
    data: List<Pair<String, Int>>,
    modifier: Modifier = Modifier
) {
    val colors = listOf(Color(0xFFF44336), Color(0xFFFF9800), Color(0xFF2196F3), Color(0xFF4CAF50))
    val total = data.sumOf { it.second }.toFloat()
    if (total == 0f) return

    val angles = data.map { it.second / total * 360f }

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceAround
    ) {
        // 圖例
        Column(verticalArrangement = Arrangement.Center) {
            data.forEachIndexed { index, (label, value) ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(modifier = Modifier.size(10.dp).background(colors[index % colors.size], CircleShape))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "$label (${(value/total * 100).toInt()}%)",
                        color = Color.White,
                        fontSize = 14.sp
                    )
                }
            }
        }

        // 圓餅圖
        Canvas(modifier = Modifier.size(150.dp)) {
            var startAngle = -90f
            angles.forEachIndexed { index, angle ->
                drawArc(
                    color = colors[index % colors.size],
                    startAngle = startAngle,
                    sweepAngle = angle,
                    useCenter = true,
                    size = Size(size.width, size.height)
                )
                startAngle += angle
            }
        }
    }
}