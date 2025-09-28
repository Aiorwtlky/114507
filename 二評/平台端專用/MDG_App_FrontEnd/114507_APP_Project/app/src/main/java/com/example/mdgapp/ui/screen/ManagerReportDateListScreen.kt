package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ManagerReportViewModel
import com.example.mdgapp.ui.component.ReportListItemCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerReportDateListScreen(
    navController: NavController,
    driverId: String?,
    viewModel: ManagerReportViewModel
) {
    LaunchedEffect(driverId) {
        driverId?.let { viewModel.selectDriver(it) }
    }

    val reports by viewModel.selectedDriverReports.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val drivers by viewModel.drivers.collectAsState()
    // 從駕駛員列表中找到當前選擇的駕駛員名稱
    val driverName = remember(driverId, drivers) {
        drivers.find { it.driverId == driverId }?.driverName ?: "駕駛"
    }

    Scaffold(
        topBar = {
            TopAppBar(
                // ✅ 顯示駕駛員名稱，讓使用者介面更清晰
                title = { Text("$driverName 的報表列表") },
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
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize().padding(paddingValues), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(paddingValues),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(reports, key = { it.date }) { report ->
                    ReportListItemCard(
                        date = report.date,
                        totalScore = report.totalScore,
                        onClick = {
                            navController.navigate("managerReportDetail/${report.date}")
                        }
                    )
                }
            }
        }
    }
}