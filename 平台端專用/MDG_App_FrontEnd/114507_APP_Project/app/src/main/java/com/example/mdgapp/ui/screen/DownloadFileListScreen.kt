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
import com.example.mdgapp.data.viewmodel.DriverDownloadViewModel
import com.example.mdgapp.ui.component.DateListItemCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DownloadFileListScreen(
    navController: NavController,
    viewModel: DriverDownloadViewModel = viewModel()
) {
    // ✅ 修正：移除 LaunchedEffect。
    // ViewModel 的 init { ... } 區塊會自動載入資料，
    // 我們不需要從 UI 手動觸發。

    val dailyLogs by viewModel.dailyLogs.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("行車影像日期") },
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
        // 為了更好的使用者體驗，在 dailyLogs 為空時，可以顯示一個載入指示器
        if (dailyLogs.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize().padding(paddingValues), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Color.White)
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
                            navController.navigate("videoList/${log.date}")
                        }
                    )
                }
            }
        }
    }
}