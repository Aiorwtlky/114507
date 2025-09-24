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
import java.time.LocalDate

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerVideoListScreen(
    navController: NavController,
    dateString: String?,
    viewModel: ManagerDownloadViewModel = viewModel()
) {
    // 這裡我們直接使用 ViewModel 中的 dailyLogs，因為它已經被上一個畫面篩選過了
    val dailyLogs by viewModel.dailyLogs.collectAsState()
    val selectedDate = remember(dateString) { dateString?.let { LocalDate.parse(it) } }
    val videosForDate = dailyLogs.find { it.date == selectedDate }?.videos ?: emptyList()

    Scaffold(
        topBar = { /* ... TopAppBar 內容與 VideoListScreen 類似 ... */ },
        containerColor = Color.Black
    ) { paddingValues ->
        if (videosForDate.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize().padding(paddingValues), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Color.White)
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(paddingValues),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(videosForDate, key = { it.id }) { video ->
                    VideoListItem(videoFile = video)
                }
            }
        }
    }
}