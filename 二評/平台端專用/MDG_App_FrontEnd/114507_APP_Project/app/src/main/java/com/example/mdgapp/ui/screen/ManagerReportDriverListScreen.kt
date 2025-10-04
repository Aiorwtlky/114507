package com.example.mdgapp.ui.screen
/*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
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
import com.example.mdgapp.data.viewmodel.ManagerReportViewModel

// 新增檔案：管理者報表第一頁 - 駕駛列表
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerReportDriverListScreen(
    navController: NavController,
    viewModel: ManagerReportViewModel = viewModel()
) {
    val drivers by viewModel.drivers.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("選擇駕駛員") },
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
        LazyColumn(
            modifier = Modifier.fillMaxSize().padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(drivers, key = { it.driverId }) { driver ->
                DriverListItemCard(
                    driver = driver,
                    onClick = {
                        // 導航到該駕駛的報表日期列表
                        navController.navigate("managerReportDateList/${driver.driverId}")
                    }
                )
            }
        }
    }
}

// 駕駛列表的卡片元件
@Composable
fun DriverListItemCard(driver: DriverInfo, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(driver.driverName, color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                Text("駕駛編號: ${driver.driverId}", color = Color.Gray, fontSize = 14.sp)
            }
            Text("最新分數: ${driver.latestScore}", color = Color.White, fontSize = 16.sp)
            Icon(
                imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                contentDescription = "選擇",
                tint = Color.White
            )
        }
    }
}*/