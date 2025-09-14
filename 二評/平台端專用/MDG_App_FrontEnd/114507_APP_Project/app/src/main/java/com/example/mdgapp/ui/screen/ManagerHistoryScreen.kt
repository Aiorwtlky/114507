package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.model.DriverInfo
import com.example.mdgapp.data.viewmodel.ManagerHistoryViewModel
import com.example.mdgapp.ui.component.HistorySection

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerHistoryScreen(
    navController: NavController,
    viewModel: ManagerHistoryViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("管理者歷史數據總覽") },
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
                // 核心數據卡片
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    MetricCard("團隊平均分數", uiState.fleetAverageScore.toString(), "分", Modifier.weight(1f))
                    MetricCard("首要風險因子", uiState.topRiskFactor, "", Modifier.weight(1f))
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    MetricCard("高風險駕駛", uiState.highRiskDriverCount.toString(), "人", Modifier.weight(1f))
                    MetricCard("本月重大事件", uiState.criticalEventsThisMonth.toString(), "次", Modifier.weight(1f))
                }

                // 駕駛員表現排名
                HistorySection(title = "表現最佳駕駛 Top 3") {
                    uiState.bestPerformingDrivers.forEach { driver ->
                        DriverRankRow(driver = driver, rankColor = Color.Green)
                    }
                }
                HistorySection(title = "最需關注駕駛") {
                    uiState.driversNeedingAttention.forEach { driver ->
                        DriverRankRow(driver = driver, rankColor = Color.Red)
                    }
                }

                // 團隊風險趨勢
                HistorySection(title = "團隊平均分數趨勢") {
                    TrendChart(
                        data = uiState.chartData,
                        labels = uiState.chartXAxisLabels,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp)
                            .padding(top = 8.dp)
                    )
                }
            }
        }
    }
}


@Composable
fun DriverRankRow(driver: DriverInfo, rankColor: Color) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(driver.driverName, color = Color.White, fontSize = 16.sp)
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("平均分數: ", color = Color.Gray, fontSize = 14.sp)
            Text(driver.latestScore.toString(), color = rankColor, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        }
    }
}