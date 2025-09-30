// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/ReportListScreen.kt

package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ReportViewModel
import com.example.mdgapp.ui.component.ReportListItemCard
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportListScreen(
    navController: NavController,
    viewModel: ReportViewModel
) {
    // 現在 reports 是 List<Trip>
    val reports by viewModel.reports.collectAsState()

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
        if (reports.isEmpty()) {
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
                    // 解析日期字串以供顯示
                    val zonedDateTime = OffsetDateTime.parse(report.startTime)
                    val date = zonedDateTime.toLocalDate()

                    ReportListItemCard(
                        date = date,
                        totalScore = report.score.toDoubleOrNull()?.toInt() ?: 0,
                        onClick = {
                            // 【修改】點擊時傳遞 report.id
                            navController.navigate("reportDetail/${report.id}")
                        }
                    )
                }
            }
        }
    }
}