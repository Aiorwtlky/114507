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
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ReportViewModel
import com.example.mdgapp.ui.component.ReportListItemCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportListScreen(
    navController: NavController,
    // ✅ 修改點：不再使用 viewModel() 建立實例，而是直接接收 viewModel 參數
    viewModel: ReportViewModel
) {
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
                items(reports, key = { it.date }) { report ->
                    ReportListItemCard(
                        date = report.date,
                        totalScore = report.totalScore,
                        onClick = {
                            navController.navigate("reportDetail/${report.date}")
                        }
                    )
                }
            }
        }
    }
}
