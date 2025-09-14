package com.example.mdgapp.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModel
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.ui.component.InteractiveLineChart
import com.example.mdgapp.ui.component.TopMenuBar
import kotlinx.coroutines.CoroutineScope


// (注意：這裡的 ManagerHomeViewModel 和 InfoCard 等相關程式碼應如我之前提供的那樣存在)
class ManagerHomeViewModel : ViewModel() {
    // ...
}

// ✅ 修正點 1: 將 ExperimentalMaterial3.class 改為 ExperimentalMaterial3Api::class
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerHomeScreen(
    navController: NavController? = null,
) {
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val coroutineScope = rememberCoroutineScope()
    var selectedTab by remember { mutableStateOf("週") }

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
            drawerState,
            coroutineScope,
            selectedTab,
            onTabSelected = { selectedTab = it },
            navController
        )
    }
}

// ✅ 修正點 2: 將 ExperimentalMaterial3.class 改為 ExperimentalMaterial3Api::class
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerMainContent(
    drawerState: DrawerState,
    coroutineScope: CoroutineScope,
    selectedTab: String,
    onTabSelected: (String) -> Unit,
    navController: NavController?
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
                    "公告" -> navController?.navigate("announcementList")
                    "下載" -> navController?.navigate("downloadFileList")
                    else -> selectedMenu = it
                }
            },
            navController = navController!!
        )

        Spacer(modifier = Modifier.height(8.dp))

        if (selectedMenu == "首頁") {
            val scrollState = rememberScrollState()
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
                    .weight(1f)
                    .verticalScroll(scrollState),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text("車隊總覽", fontSize = 22.sp, color = Color.White)
                Row(Modifier.fillMaxWidth(), Arrangement.spacedBy(12.dp)) {
                    InfoCard(value = 15, label = "在線駕駛員", fillColor = Color.Green, backgroundColor = Color.DarkGray, modifier = Modifier.weight(1f))
                    InfoCard(value = 82, label = "車隊平均分數", fillColor = Color.Cyan, backgroundColor = Color.DarkGray, modifier = Modifier.weight(1f))
                }
                Row(Modifier.fillMaxWidth(), Arrangement.spacedBy(12.dp)) {
                    InfoCard(value = 128, label = "今日趟次", fillColor = Color.Yellow, backgroundColor = Color.DarkGray, modifier = Modifier.weight(1f))
                    InfoCard(value = 3, label = "異常事件", fillColor = Color.Red, backgroundColor = Color.DarkGray, modifier = Modifier.weight(1f))
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text("平均分數趨勢", fontSize = 22.sp, color = Color.White)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    TabItem("月", selectedTab == "月") { onTabSelected("月") }
                    TabItem("週", selectedTab == "週") { onTabSelected("週") }
                    TabItem("日", selectedTab == "日") { onTabSelected("日") }
                }
                InteractiveLineChart(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                        .padding(vertical = 8.dp),
                    selectedTab = selectedTab
                )
            }
        }

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
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                NavigationItem(R.drawable.ic_list, "駕駛列表") {
                    // navController?.navigate("driverList")
                }
                NavigationItem(R.drawable.ic_group, "車隊總覽") {
                    // navController?.navigate("fleetOverview")
                }
                NavigationItem(R.drawable.ic_post, "報表") {
                    navController?.navigate("managerReportDriverList")
                }
                NavigationItem(R.drawable.ic_person, "設定") {
                    navController?.navigate("managerSettings")
                }
            }
        }
    }
}