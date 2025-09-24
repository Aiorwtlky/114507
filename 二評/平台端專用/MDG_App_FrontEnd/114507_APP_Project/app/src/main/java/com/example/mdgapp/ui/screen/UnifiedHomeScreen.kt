package com.example.mdgapp.ui.screen

import android.content.Context
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
import androidx.compose.ui.platform.LocalContext
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
import kotlinx.coroutines.launch
import java.time.format.DateTimeFormatter
import com.example.mdgapp.ui.component.TrendChart
import com.example.mdgapp.ui.component.GaugeScoreCard

// =================================================================================
// 主要的 UnifiedHomeScreen Composable
// =================================================================================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UnifiedHomeScreen(
    navController: NavController,
    userRole: String,
    viewModel: HomeViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val coroutineScope = rememberCoroutineScope()

    Scaffold(
        topBar = {
            HomeTopBar(
                navController = navController,
                userRole = userRole,
                onAvatarClick = {
                    coroutineScope.launch { drawerState.open() }
                }
            )
        },
        bottomBar = {
            AppBottomBar(navController = navController, userRole = userRole)
        },
        containerColor = Color.Black
    ) { paddingValues ->
        DashboardContent(
            uiState = uiState,
            viewModel = viewModel,
            // ✅ 修正 #1: 將 NavController 傳入 DashboardContent
            navController = navController,
            modifier = Modifier.padding(paddingValues)
        )
    }
}

// =================================================================================
// 頂部導覽列 (頭像、公告、下載)
// =================================================================================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun HomeTopBar(
    navController: NavController,
    userRole: String,
    onAvatarClick: () -> Unit
) {
    TopAppBar(
        title = {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // 將頭像的 IconButton 直接放入 Row 中
                IconButton(onClick = onAvatarClick) {
                    Image(
                        painter = painterResource(id = R.drawable.jiboda1),
                        contentDescription = "頭像",
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                    )
                }

                Spacer(modifier = Modifier.width(16.dp)) // 頭像與按鈕的間距

                // 公告與下載按鈕
                Button(
                    onClick = {
                        val route = if (userRole == "manager") "managerAnnouncementList" else "announcementList"
                        navController.navigate(route)
                    },
                    shape = CircleShape,
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White, contentColor = Color.Black),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) { Text("公告") }

                Spacer(modifier = Modifier.width(8.dp))

                Button(
                    onClick = {
                        val route = if (userRole == "manager") "managerDriverSelectionForDownload" else "downloadFileList"
                        navController.navigate(route)
                    },
                    shape = CircleShape,
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White, contentColor = Color.Black),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) { Text("下載") }
            }
        },
        // 將 navigationIcon 留空，因為頭像已經移到 title 區塊
        navigationIcon = {},
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = Color.Black
        ),
        // 設定 padding 來確保最左邊的頭像與螢幕邊緣有間距
        windowInsets = TopAppBarDefaults.windowInsets.exclude(WindowInsets.navigationBars)
            .add(WindowInsets(left = 6.dp))
    )
}

// =================================================================================
// 儀表板內容 (Dashboard Content)
// =================================================================================
@Composable
private fun DashboardContent(
    uiState: HomeUiState,
    viewModel: HomeViewModel,
    // ✅ 修正 #2: DashboardContent 接收 NavController
    navController: NavController,
    modifier: Modifier = Modifier
) {
    if (uiState.isLoading) {
        Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
    } else {
        Column(
            modifier = modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // ✅ 修正 #3: 正確傳遞 NavController，移除 applicationContext 錯誤
            uiState.lastTrip?.let { LastTripCard(it, navController = navController) }
            PastAverageCard(
                data = uiState.pastAverage,
                onTimeUnitSelected = viewModel::onAverageTimeUnitSelected,
                onValueSelected = viewModel::onAverageValueSelected
            )
            PastTrendCard(
                data = uiState.pastTrend,
                onTimeUnitSelected = viewModel::onTrendTimeUnitSelected,
                onValueSelected = viewModel::onTrendValueSelected
            )
        }
    }
}

// =================================================================================
// ✅ 修正 #4: 重新加入被誤刪的三大卡片 Composable
// =================================================================================

@Composable
fun LastTripCard(lastTrip: LastTripInfo, navController: NavController) {
    val purpleButtonColors = ButtonDefaults.buttonColors(
        containerColor = Color(0xFF6A1B9A),
        contentColor = Color.Black
    )
    val dateFormatter = DateTimeFormatter.ofPattern("yyyy/MM/dd")

    Card(
        modifier = Modifier.padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.DarkGray)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("前次行程", style = MaterialTheme.typography.titleLarge, color = Color.White)
            Divider(color = Color.Gray)
            Text("行程日期: ${lastTrip.startTime.format(dateFormatter)}", fontSize = 14.sp, color = Color.White)
            Text("總耗時: ${lastTrip.duration.toMinutes()} 分鐘", fontSize = 14.sp, color = Color.White)
            Text("路線: ${lastTrip.startLocation} - ${lastTrip.endLocation} (${lastTrip.mileage} km)", fontSize = 14.sp, color = Color.White)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("安全總分: ", style = MaterialTheme.typography.bodyLarge, color = Color.White)
                Text("${lastTrip.totalScore}", color = Color.Cyan, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.width(8.dp))
                Text("(進步 ${lastTrip.improvementPercentage}%)", color = Color.Green, fontSize = 14.sp)
            }
            Column {
                Text("違規項目:", fontWeight = FontWeight.Bold, color = Color.White)
                lastTrip.violations.forEach {
                    Text("  - ${it.item} (扣 ${it.scoreDeduction} 分)", color = Color.Red)
                }
            }
            Text("AI 行車建議: ${lastTrip.aiSuggestion}", style = MaterialTheme.typography.bodySmall, color = Color.LightGray)
            Button(
                onClick = { /* navController.navigate(...) */ },
                modifier = Modifier.align(Alignment.End),
                colors = purpleButtonColors
            ) {
                Text("查看完整建議", color = Color.White)
            }
        }
    }
}

@Composable
fun PastAverageCard(
    data: PastAverageData,
    onTimeUnitSelected: (String) -> Unit,
    onValueSelected: (String) -> Unit
) {
    Card(
        modifier = Modifier.padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.DarkGray)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("過往平均", style = MaterialTheme.typography.titleLarge, color = Color.White)
            ChartFilterMenus(
                timeUnitOptions = data.timeUnitOptions,
                selectedTimeUnit = data.selectedTimeUnit,
                valueOptions = data.valueOptions,
                selectedValue = data.selectedValue,
                onTimeUnitSelected = onTimeUnitSelected,
                onValueSelected = onValueSelected
            )
            Spacer(modifier = Modifier.height(8.dp))
            // ✅ 修正 #2: 移除佔位 Box，呼叫您提供的 GaugeScoreCard 元件
            GaugeScoreCard(
                score = data.averageScore,
                label = "平均駕駛行為分數",
                modifier = Modifier
                    .fillMaxWidth()
                    .height(150.dp) // 您可以調整適合的高度
            )
        }
    }
}

@Composable
fun PastTrendCard(data: PastTrendData, onTimeUnitSelected: (String) -> Unit, onValueSelected: (String) -> Unit) {
    Card(
        modifier = Modifier.padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.DarkGray)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("過往趨勢圖表", style = MaterialTheme.typography.titleLarge, color = Color.White)
            ChartFilterMenus(
                timeUnitOptions = data.timeUnitOptions,
                selectedTimeUnit = data.selectedTimeUnit,
                valueOptions = data.valueOptions,
                selectedValue = data.selectedValue,
                onTimeUnitSelected = onTimeUnitSelected,
                onValueSelected = onValueSelected
            )
            Spacer(modifier = Modifier.height(16.dp))

            // ✅ 修正 #3: 呼叫 TrendChart 時，傳入 labels 參數
            TrendChart(
                data = data.chartData,
                labels = data.chartLabels, // 傳入水平座標軸標籤
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
            )
        }
    }
}