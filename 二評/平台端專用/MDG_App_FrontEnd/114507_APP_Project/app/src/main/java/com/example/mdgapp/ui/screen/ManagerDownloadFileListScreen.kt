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
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ManagerDownloadViewModel
import com.example.mdgapp.ui.component.DateListItemCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerDownloadFileListScreen(
    navController: NavController,
    driverId: String?,
    viewModel: ManagerDownloadViewModel = viewModel()
) {
    LaunchedEffect(driverId) {
        driverId?.let { viewModel.loadDailyLogsForDriver(it) }
    }

    val dailyLogs by viewModel.dailyLogs.collectAsState()
    val drivers by viewModel.drivers.collectAsState()
    val driverName = drivers.find { it.driverId == driverId }?.driverName ?: ""

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("$driverName 的行車影像日期") },
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
        if (dailyLogs.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize().padding(paddingValues), contentAlignment = Alignment.Center) {
                if (!driverId.isNullOrEmpty()) CircularProgressIndicator(color = Color.White)
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(paddingValues),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(dailyLogs, key = { it.date }) { log ->
                    DateListItemCard(
                        date = log.date,
                        videoCount = log.videos.size,
                        onClick = {
                            // 導航到管理者專屬的影片列表，並傳遞 driverId 和 date
                            navController.navigate("managerVideoList/${driverId}/${log.date}")
                        }
                    )
                }
            }
        }
    }
}