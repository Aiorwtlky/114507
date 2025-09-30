// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/ManagerReportDateListScreen.kt

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
import java.time.OffsetDateTime

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

    val driverName = remember(driverId, drivers) {
        drivers.find { it.driverId == driverId }?.driverName ?: "駕駛"
    }

    Scaffold(
        topBar = {
            TopAppBar(
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
                items(reports, key = { it.id }) { report ->
                    val zonedDateTime = OffsetDateTime.parse(report.startTime)
                    val date = zonedDateTime.toLocalDate()
                    val score = report.score.toDoubleOrNull()?.toInt() ?: 0

                    ReportListItemCard(
                        date = date,
                        totalScore = score,
                        onClick = {
                            navController.navigate("managerReportDetail/${report.id}")
                        }
                    )
                }
            }
        }
    }
}