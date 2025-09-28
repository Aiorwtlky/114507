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
import com.example.mdgapp.ui.component.ChartFilterMenus
import com.example.mdgapp.ui.component.GaugeScoreCard
import com.example.mdgapp.ui.component.TrendChart
import kotlinx.coroutines.launch
import java.time.format.DateTimeFormatter
import android.util.Log // ✅ 確認已 import Log

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
                IconButton(onClick = onAvatarClick) {
                    Image(
                        painter = painterResource(id = R.drawable.jiboda1),
                        contentDescription = "頭像",
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))
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
                        // 修改點：管理者點擊下載，現在是查看自己的下載列表
                        val route = if (userRole == "manager") "managerSelfDownloadList" else "downloadFileList"
                        navController.navigate(route)
                    },
                    shape = CircleShape,
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White, contentColor = Color.Black),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) { Text("下載") }
            }
        },
        navigationIcon = {},
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = Color.Black
        ),
        windowInsets = TopAppBarDefaults.windowInsets.exclude(WindowInsets.navigationBars)
            .add(WindowInsets(left = 16.dp))
    )
}

// =================================================================================
// 底部功能列元件
// =================================================================================
@Composable
fun AppBottomBar(navController: NavController, userRole: String) {
    NavigationBar(
        containerColor = Color.Black
    ) {
        val labelFontSize = 12.sp
        val iconSize = 24.dp
        val itemColors = NavigationBarItemDefaults.colors(
            indicatorColor = Color.Transparent,
            unselectedIconColor = Color.White,
            unselectedTextColor = Color.White
        )

        NavigationBarItem(
            selected = false,
            onClick = {
                // ✅ 在這裡加入 Log
                Log.d("NavigationCheck", "行駛軌跡按鈕被點擊，準備導航至 routeTracking")
                navController.navigate("routeTracking") },
            icon = { Icon(painterResource(id = R.drawable.ic_map), "行駛軌跡", modifier = Modifier.size(iconSize)) },
            label = { Text("行駛軌跡", fontSize = labelFontSize) },
            colors = itemColors
        )
        NavigationBarItem(
            selected = false,
            onClick = {
                // 修改點：駕駛員現在導航到唯讀的群組頁面
                val route = if (userRole == "manager") "groupManagement" else "driverGroupScreen"
                navController.navigate(route)
            },
            icon = { Icon(painterResource(id = R.drawable.ic_group), "群組", modifier = Modifier.size(iconSize)) },
            label = { Text("群組", fontSize = labelFontSize) },
            colors = itemColors
        )
        NavigationBarItem(
            selected = false,
            onClick = { navController.navigate("qrScan") },
            icon = { Icon(painterResource(id = R.drawable.ic_qr), "打卡", modifier = Modifier.size(iconSize)) },
            label = { Text("打卡", fontSize = labelFontSize) },
            colors = itemColors
        )
        NavigationBarItem(
            selected = false,
            onClick = {
                // 修改點：管理者點擊報表，現在是查看自己的報表列表
                val route = if (userRole == "manager") "managerSelfReportList" else "reportList"
                navController.navigate(route)
            },
            icon = { Icon(painterResource(id = R.drawable.ic_post), "報表", modifier = Modifier.size(iconSize)) },
            label = { Text("報表", fontSize = labelFontSize) },
            colors = itemColors
        )
        NavigationBarItem(
            selected = false,
            onClick = {
                val route = if (userRole == "manager") "managerProfile" else "profile"
                navController.navigate(route)
            },
            icon = { Icon(painterResource(id = R.drawable.ic_person), "我的", modifier = Modifier.size(iconSize)) },
            label = { Text("我的", fontSize = labelFontSize) },
            colors = itemColors
        )
    }
}

// =================================================================================
// 儀表板與卡片內容 (為保持檔案完整性而附上，內容不變)
// =================================================================================
@Composable
private fun DashboardContent(uiState: HomeUiState, viewModel: HomeViewModel, navController: NavController, modifier: Modifier = Modifier) {
    if (uiState.isLoading) {
        Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
    } else {
        Column(
            modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(bottom = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
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

@Composable
fun LastTripCard(lastTrip: LastTripInfo, navController: NavController) {
    Card(
        modifier = Modifier.padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.DarkGray)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("前次行程", style = MaterialTheme.typography.titleLarge, color = Color.White)
            Divider(color = Color.Gray)
            Text("行程日期: ${lastTrip.startTime.format(DateTimeFormatter.ofPattern("yyyy/MM/dd"))}", fontSize = 14.sp, color = Color.White)
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
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF6A1B9A))
            ) {
                Text("查看完整建議", color = Color.White)
            }
        }
    }
}

@Composable
fun PastAverageCard(data: PastAverageData, onTimeUnitSelected: (String) -> Unit, onValueSelected: (String) -> Unit) {
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
            GaugeScoreCard(
                score = data.averageScore,
                label = "平均駕駛行為分數",
                modifier = Modifier.fillMaxWidth().height(150.dp)
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
            TrendChart(
                data = data.chartData,
                labels = data.chartLabels,
                modifier = Modifier.fillMaxWidth().height(200.dp)
            )
        }
    }
}