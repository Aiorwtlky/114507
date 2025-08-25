package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.DownloadViewModel
import com.example.mdgapp.ui.component.TimeSlotHeader
import com.example.mdgapp.ui.component.VideoFileCard
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import androidx.compose.runtime.remember

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VideoListScreen(
    navController: NavController,
    dateString: String?,
    viewModel: DownloadViewModel = viewModel()
) {
    // 解析從導航傳來的日期字串
    val selectedDate = remember(dateString) {
        dateString?.let { LocalDate.parse(it) }
    }

    // 當 selectedDate 發生變化時，通知 ViewModel 更新其狀態
    LaunchedEffect(selectedDate) {
        selectedDate?.let {
            viewModel.selectDate(it)
        }
    }

    val selectedLog by viewModel.selectedDateLog.collectAsState()
    val groupedVideos = selectedLog?.videos?.groupBy { it.timestamp.hour / 3 }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    val formattedDate = selectedDate?.format(DateTimeFormatter.ofPattern("yyyy / MM / dd")) ?: "載入中..."
                    Text(formattedDate)
                },
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
        if (groupedVideos == null) {
            Box(modifier = Modifier.fillMaxSize().padding(paddingValues), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Color.White)
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(paddingValues),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                groupedVideos.toSortedMap().forEach { (timeSlotIndex, videos) ->
                    item {
                        TimeSlotHeader(timeSlotIndex = timeSlotIndex)
                    }
                    items(videos) { video ->
                        VideoFileCard(videoFile = video)
                        Spacer(modifier = Modifier.height(8.dp))
                    }
                }
            }
        }
    }
}
