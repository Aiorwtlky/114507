package com.example.mdgapp.ui.screen

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
// ✅ 修正 2：新增 Brush 的 import
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.data.viewmodel.ManagerHomeViewModel
import com.example.mdgapp.ui.component.InfoCard
import com.example.mdgapp.ui.component.TopMenuBar
import com.example.mdgapp.ui.component.TrendChart
import kotlinx.coroutines.CoroutineScope

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerHomeScreen(
    navController: NavController,
    viewModel: ManagerHomeViewModel = viewModel()
) {
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val coroutineScope = rememberCoroutineScope()
    val uiState by viewModel.uiState.collectAsState()

    ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = true,
        drawerContent = {
            ModalDrawerSheet(
                modifier = Modifier
                    .fillMaxHeight()
                    .width(268.dp),
                drawerContainerColor = Color(0xFF1C1C1C),
                drawerContentColor = Color.White
            ) {
                Spacer(Modifier.height(24.dp))
                Text("選單", modifier = Modifier.padding(16.dp), fontSize = 20.sp)
                HorizontalDivider()
                DrawerItem("系統設定")
                DrawerItem("關於我們")
            }
        }
    ) {
        ManagerMainContent(
            drawerState = drawerState,
            coroutineScope = coroutineScope,
            uiState = uiState,
            onTabSelected = { viewModel.onTabSelected(it) },
            navController = navController
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerMainContent(
    drawerState: DrawerState,
    coroutineScope: CoroutineScope,
    uiState: com.example.mdgapp.data.viewmodel.ManagerHomeUiState,
    onTabSelected: (String) -> Unit,
    navController: NavController
) {
    var selectedMenu by remember { mutableStateOf("首頁") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        TopMenuBar(
            coroutineScope = coroutineScope,
            drawerState = drawerState,
            selectedMenu = selectedMenu,
            onMenuSelected = {
                selectedMenu = it
                when (it) {
                    // ✅ 修正：將導覽路徑指向管理者專用的公告列表
                    "公告" -> navController.navigate("managerAnnouncementList")
                    "下載" -> navController.navigate("downloadFileList")
                    else -> selectedMenu = it
                }
            },
            navController = navController
        )

        // ... 以下中間內容和底部導覽列都保持不變 ...
        if (selectedMenu == "首頁") {
            if (uiState.isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .weight(1f)
                        .verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Text("車隊總覽", fontSize = 22.sp, color = Color.White)
                    Row(Modifier.fillMaxWidth(), Arrangement.spacedBy(12.dp)) {
                        InfoCard(value = uiState.onlineDrivers, label = "在線駕駛員", fillColor = Color.Green, backgroundColor = Color.DarkGray, modifier = Modifier.weight(1f))
                        InfoCard(value = uiState.fleetAverageScore, label = "車隊平均分數", fillColor = Color.Cyan, backgroundColor = Color.DarkGray, modifier = Modifier.weight(1f))
                    }
                    Row(Modifier.fillMaxWidth(), Arrangement.spacedBy(12.dp)) {
                        InfoCard(value = uiState.tripsToday, label = "今日趟次", fillColor = Color.Yellow, backgroundColor = Color.DarkGray, modifier = Modifier.weight(1f))
                        InfoCard(value = uiState.eventsToday, label = "今日異常", fillColor = Color.Red, backgroundColor = Color.DarkGray, modifier = Modifier.weight(1f))
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("平均分數趨勢", fontSize = 22.sp, color = Color.White)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        TabItem("月", uiState.selectedTab == "月", onClick = { onTabSelected("月") })
                        TabItem("週", uiState.selectedTab == "週", onClick = { onTabSelected("週") })
                        TabItem("日", uiState.selectedTab == "日", onClick = { onTabSelected("日") })
                    }

                    TrendChart(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp)
                            .padding(vertical = 8.dp),
                        data = uiState.chartData,
                        labels = uiState.chartXAxisLabels
                    )
                }
            }
        }

        // 底部導覽列
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(80.dp)
        ) {
            Box(
                modifier = Modifier
                    .matchParentSize()
                    .background(
                        brush = Brush.verticalGradient(
                            colors = listOf(Color.Black.copy(alpha = 0.6f), Color.Transparent),
                            startY = 0f,
                            endY = 80f
                        )
                    )
            )
            Row(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 24.dp),
                horizontalArrangement = Arrangement.SpaceAround,
                verticalAlignment = Alignment.CenterVertically
            ) {
                NavigationItem(R.drawable.ic_group, "群組管理") {
                    navController.navigate("groupManagement")
                }
                NavigationItem(R.drawable.ic_post, "報表") {
                    navController.navigate("managerReportDriverList")
                }
                NavigationItem(R.drawable.ic_analyze, "歷史數據") {
                    navController.navigate("managerHistory")
                }
                NavigationItem(R.drawable.ic_person, "設定") {
                    navController.navigate("managerProfile")
                }
            }
        }
    }
}