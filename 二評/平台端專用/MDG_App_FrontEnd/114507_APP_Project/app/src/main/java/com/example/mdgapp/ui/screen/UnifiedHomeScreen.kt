package com.example.mdgapp.ui.screen

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.data.viewmodel.*
import com.example.mdgapp.ui.component.AppBottomBar
import com.example.mdgapp.ui.component.ChartFilterMenus
import com.example.mdgapp.ui.component.GaugeScoreCard
import com.example.mdgapp.ui.component.TrendChart
import kotlinx.coroutines.launch
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UnifiedHomeScreen(
    navController: NavController,
    viewModel: HomeViewModel = viewModel(),
    // ✅ 1. 新增 reportViewModel 參數以接收從 AppNavGraph 傳來的資料
    reportViewModel: ReportViewModel
) {
    val uiState by viewModel.uiState.collectAsState()
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val coroutineScope = rememberCoroutineScope()

    Scaffold(
        topBar = {
            HomeTopBar(
                navController = navController,
                onAvatarClick = {
                    coroutineScope.launch { drawerState.open() }
                }
            )
        },
        bottomBar = {
            AppBottomBar(navController = navController)
        },
        containerColor = Color.Black
    ) { paddingValues ->
        DashboardContent(
            uiState = uiState,
            homeViewModel = viewModel,
            // ✅ 2. 將 reportViewModel 傳遞給 DashboardContent
            reportViewModel = reportViewModel,
            navController = navController,
            modifier = Modifier.padding(paddingValues)
        )
    }
}

// HomeTopBar 和 AppBottomBar 保持不變
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun HomeTopBar(navController: NavController, onAvatarClick: () -> Unit) { /* ... 內容不變 ... */ }

@Composable
fun AppBottomBar(navController: NavController) { /* ... 內容不變 ... */ }


@Composable
private fun DashboardContent(
    uiState: HomeUiState,
    homeViewModel: HomeViewModel,
    // ✅ 3. DashboardContent 接收 reportViewModel
    reportViewModel: ReportViewModel,
    navController: NavController,
    modifier: Modifier = Modifier
) {
    if (uiState.isLoading) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
    } else {
        Column(
            modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(bottom = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // ✅ 4. 將 reportViewModel 傳遞給 LastTripCard
            uiState.lastTrip?.let { LastTripCard(it, navController = navController, reportViewModel = reportViewModel) }
            PastAverageCard(
                data = uiState.pastAverage,
                onTimeUnitSelected = homeViewModel::onAverageTimeUnitSelected,
                onValueSelected = homeViewModel::onAverageValueSelected
            )
            PastTrendCard(
                data = uiState.pastTrend,
                onTimeUnitSelected = homeViewModel::onTrendTimeUnitSelected,
                onValueSelected = homeViewModel::onTrendValueSelected
            )
        }
    }
}

@Composable
fun LastTripCard(
    lastTrip: LastTripInfo,
    navController: NavController,
    // ✅ 5. LastTripCard 接收 reportViewModel
    reportViewModel: ReportViewModel
) {
    // 觀察報表列表的狀態
    val reports by reportViewModel.reports.collectAsState()

    Card(
        modifier = Modifier.padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.DarkGray)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            // ... (卡片上半部內容不變)

            Button(
                onClick = {
                    // 從報表列表中取得最新一筆資料的日期
                    val latestReportDate = reports.firstOrNull()?.date
                    if (latestReportDate != null) {
                        navController.navigate("reportDetail/${latestReportDate}")
                    }
                },
                modifier = Modifier.align(Alignment.End),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF6A1B9A))
            ) {
                Text("查看完整建議", color = Color.White)
            }
        }
    }
}

// PastAverageCard 和 PastTrendCard 保持不變
@Composable
fun PastAverageCard(data: PastAverageData, onTimeUnitSelected: (String) -> Unit, onValueSelected: (String) -> Unit) { /* ... 內容不變 ... */ }

@Composable
fun PastTrendCard(data: PastTrendData, onTimeUnitSelected: (String) -> Unit, onValueSelected: (String) -> Unit) { /* ... 內容不變 ... */ }