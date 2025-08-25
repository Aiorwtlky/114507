package com.example.mdgapp.ui.screen

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.data.model.UploadedFile
import com.example.mdgapp.ui.component.GaugeScoreCard
import com.example.mdgapp.ui.component.InteractiveLineChart
import com.example.mdgapp.ui.component.TopMenuBar
import com.example.mdgapp.ui.theme.MyApplicationTheme
import kotlinx.coroutines.CoroutineScope

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(navController: NavController? = null) {
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
                DrawerItem("FAQ")
                DrawerItem("關於我們")
                DrawerItem("設定")
            }
        }
    ) {
        MainContent(
            drawerState,
            coroutineScope,
            selectedTab,
            onTabSelected = { selectedTab = it },
            navController
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainContent(
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
        // 上方選單列
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
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Row(Modifier.fillMaxWidth(), Arrangement.spacedBy(12.dp)) {
                    GaugeScoreCard(score = 30, label = "駕駛行為分數", modifier = Modifier.weight(1f))
                }
                Row(Modifier.fillMaxWidth(), Arrangement.spacedBy(12.dp)) {
                    GaugeScoreCard(score = 86, label = "平均駕駛行為分數", modifier = Modifier.weight(1f))
                }

                Text("平均分數", fontSize = 22.sp, color = Color.White)
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
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                NavigationItem(R.drawable.ic_map, "行駛軌跡") {
                    navController?.navigate("routeTracking")
                }
                // --- ✅ 修改開始 ---
                NavigationItem(R.drawable.ic_list, "報表") {
                    navController?.navigate("reportList")
                }
                // --- ✅ 修改結束 ---
                NavigationItem(R.drawable.ic_qr, "打卡") {
                    navController?.navigate("qrScan")
                }
                NavigationItem(R.drawable.ic_person, "我的")
            }
        }
    }
}

@Composable
fun TabItem(title: String, selected: Boolean, onClick: () -> Unit) {
    Surface(
        shape = RoundedCornerShape(8.dp),
        color = if (selected) Color.White else Color.Black,
        border = BorderStroke(1.dp, Color.Gray),
        modifier = Modifier.clickable { onClick() }
    ) {
        Text(
            text = title,
            color = if (selected) Color.Black else Color.White,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
        )
    }
}

@Composable
fun NavigationItem(
    icon: Int,
    label: String,
    selected: Boolean = false,
    onClick: (() -> Unit)? = null
) {
    val color = if (selected) Color.White else Color.Gray
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .padding(horizontal = 8.dp)
            .clickable(enabled = onClick != null) { onClick?.invoke() }
    ) {
        Icon(
            painter = painterResource(id = icon),
            contentDescription = label,
            tint = color,
            modifier = Modifier.size(if (selected) 30.dp else 26.dp)
        )
        Text(
            text = label,
            color = color,
            fontSize = if (selected) 14.sp else 12.sp
        )
    }
}

@Composable
fun DrawerItem(text: String, onClick: () -> Unit = {}) {
    Text(
        text = text,
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
            .padding(16.dp),
        fontSize = 18.sp,
        color = Color.White
    )
}

@Composable
fun InfoCard(
    value: Int,
    label: String,
    fillColor: Color,
    backgroundColor: Color,
    modifier: Modifier = Modifier
) {
    val progress = (value.coerceIn(0, 100)) / 100f

    Card(
        modifier = modifier.height(100.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        elevation = CardDefaults.cardElevation(4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text("$value", color = Color.White, fontSize = 18.sp)
            Text(label, color = Color.Gray, fontSize = 12.sp)
            LinearProgressIndicator(
                progress = progress,
                color = fillColor,
                trackColor = backgroundColor,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .clip(RoundedCornerShape(4.dp))
            )
        }
    }
}

@Preview(showBackground = true)
@Composable
fun PreviewHomeScreen() {
    MyApplicationTheme {
        HomeScreen()
    }
}
