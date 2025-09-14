package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ManagerReportViewModel
import com.example.mdgapp.ui.component.ReportListItemCard

// 新增檔案：管理者報表第二頁 - 報表日期列表
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerReportDateListScreen(
    navController: NavController,
    driverId: String?,
    viewModel: ManagerReportViewModel // 直接接收共享的 ViewModel
) {
    // 觸發 ViewModel 根據 driverId 載入對應的報表
    LaunchedEffect(driverId) {
        driverId?.let { viewModel.selectDriver(it) }
    }

    val reports by viewModel.selectedDriverReports.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("駕駛報表列表") },
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
            items(reports, key = { it.date }) { report ->
                // 重用現有的 ReportListItemCard 元件
                ReportListItemCard(
                    date = report.date,
                    totalScore = report.totalScore,
                    onClick = {
                        // 導航到報表詳情頁
                        navController.navigate("managerReportDetail/${report.date}")
                    }
                )
            }
        }
    }
}