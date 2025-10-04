package com.example.mdgapp.ui.screen

import android.widget.Toast
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
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
import com.example.mdgapp.ui.component.ChartFilterMenus
import com.example.mdgapp.ui.component.GaugeScoreCard
import com.example.mdgapp.ui.component.TrendChart
import kotlinx.coroutines.launch
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UnifiedHomeScreen(
    navController: NavController,
    homeViewModel: HomeViewModel = viewModel(),
    reportViewModel: ReportViewModel = viewModel()
) {
    val uiState by homeViewModel.uiState.collectAsState()
    val reports by reportViewModel.reports.collectAsState()
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val coroutineScope = rememberCoroutineScope()

    // 當 ReportViewModel 的資料載入後，自動更新 HomeViewModel
    LaunchedEffect(reports) {
        if (reports.isNotEmpty()) {
            homeViewModel.setLastTrip(reports.first())
        }
    }

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
            homeViewModel = homeViewModel,
            navController = navController,
            modifier = Modifier.padding(paddingValues)
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun HomeTopBar(
    navController: NavController,
    onAvatarClick: () -> Unit
) {
    TopAppBar(
        title = {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onAvatarClick) {
                    Icon(
                        painter = painterResource(id = R.drawable.ic_person),
                        contentDescription = "頭像",
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape),
                        tint = Color.White
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))
                Button(
                    onClick = { navController.navigate("downloadFileList") },
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

@Composable
fun AppBottomBar(navController: NavController) {
    NavigationBar(containerColor = Color.Black) {
        val labelFontSize = 12.sp
        val iconSize = 24.dp
        val itemColors = NavigationBarItemDefaults.colors(
            indicatorColor = Color.Transparent,
            unselectedIconColor = Color.White,
            unselectedTextColor = Color.White
        )
        NavigationBarItem(
            selected = false,
            onClick = { navController.navigate("driverGroupScreen") },
            icon = { Icon(painterResource(id = R.drawable.ic_group), "群組", modifier = Modifier.size(iconSize)) },
            label = { Text("群組", fontSize = labelFontSize) },
            colors = itemColors
        )
        NavigationBarItem(
            selected = false,
            onClick = { navController.navigate("checkIn") },
            icon = { Icon(Icons.Filled.Check, "打卡", modifier = Modifier.size(iconSize)) },
            label = { Text("打卡", fontSize = labelFontSize) },
            colors = itemColors
        )
        NavigationBarItem(
            selected = false,
            onClick = { navController.navigate("reportList") },
            icon = { Icon(painterResource(id = R.drawable.ic_post), "報表", modifier = Modifier.size(iconSize)) },
            label = { Text("報表", fontSize = labelFontSize) },
            colors = itemColors
        )
        NavigationBarItem(
            selected = false,
            onClick = { navController.navigate("profile") },
            icon = { Icon(painterResource(id = R.drawable.ic_person), "我的", modifier = Modifier.size(iconSize)) },
            label = { Text("我的", fontSize = labelFontSize) },
            colors = itemColors
        )
    }
}


@Composable
private fun DashboardContent(
    uiState: HomeUiState,
    homeViewModel: HomeViewModel,
    navController: NavController,
    modifier: Modifier = Modifier
) {
    if (uiState.isLoading) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
    } else {
        Column(
            modifier = modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            uiState.lastTrip?.let { LastTripCard(it, navController = navController) }
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
    navController: NavController
) {
    Card(
        modifier = Modifier.padding(horizontal = 16.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.DarkGray)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            val hours = lastTrip.duration.toHours()
            val minutes = lastTrip.duration.toMinutes() % 60
            val durationText = if (hours > 0) "${hours} 小時 ${minutes} 分鐘" else "${minutes} 分鐘"

            Text("前次行程", style = MaterialTheme.typography.titleLarge, color = Color.White)
            HorizontalDivider(color = Color.Gray)
            Text("行程日期: ${lastTrip.startTime.format(DateTimeFormatter.ofPattern("yyyy/MM/dd"))}", fontSize = 14.sp, color = Color.White)
            Text("總耗時: $durationText", fontSize = 14.sp, color = Color.White)
            Text("路線: ${lastTrip.startLocation} - ${lastTrip.endLocation} (${lastTrip.mileage} km)", fontSize = 14.sp, color = Color.White)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("安全總分: ", style = MaterialTheme.typography.bodyLarge, color = Color.White)
                Text("${lastTrip.totalScore}", color = Color.Cyan, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.width(8.dp))
                val improvementText = if (lastTrip.improvementPercentage >= 0) "進步 ${lastTrip.improvementPercentage}%" else "退步 ${Math.abs(lastTrip.improvementPercentage)}%"
                val improvementColor = if (lastTrip.improvementPercentage >= 0) Color.Green else Color.Red
                Text("($improvementText)", color = improvementColor, fontSize = 14.sp)
            }
            Column {
                Text("違規項目:", fontWeight = FontWeight.Bold, color = Color.White)
                if (lastTrip.violations.isEmpty()) {
                    Text("  - 無", color = Color.Green)
                } else {
                    lastTrip.violations.forEach {
                        Text("  - ${it.item} (扣 ${it.scoreDeduction} 分)", color = Color.Yellow)
                    }
                }
            }
            Text("AI 行車建議: ${lastTrip.aiSuggestion}", style = MaterialTheme.typography.bodySmall, color = Color.LightGray)
            Button(
                onClick = {
                    val reportDate = lastTrip.startTime.toLocalDate().toString()
                    navController.navigate("reportDetail/${reportDate}")
                },
                modifier = Modifier.align(Alignment.End),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF6A1B9A))
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
            GaugeScoreCard(
                score = data.averageScore,
                label = "平均駕駛行為分數",
                modifier = Modifier.fillMaxWidth().height(150.dp)
            )
        }
    }
}

@Composable
fun PastTrendCard(
    data: PastTrendData,
    onTimeUnitSelected: (String) -> Unit,
    onValueSelected: (String) -> Unit
) {
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