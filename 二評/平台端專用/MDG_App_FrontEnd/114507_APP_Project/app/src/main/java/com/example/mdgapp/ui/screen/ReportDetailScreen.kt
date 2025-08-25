package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import com.example.mdgapp.data.viewmodel.ReportViewModel
import com.example.mdgapp.ui.component.*
import java.time.LocalDate

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportDetailScreen(
    navController: NavController,
    dateString: String?,
    // ✅ 修改點：同樣改為直接接收 viewModel 參數
    viewModel: ReportViewModel
) {
    val selectedDate = remember(dateString) { dateString?.let { LocalDate.parse(it) } }

    LaunchedEffect(selectedDate) {
        selectedDate?.let { viewModel.selectReportByDate(it) }
    }

    val report by viewModel.selectedReport.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("駕駛行為報表") },
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
        bottomBar = {
            Surface(color = Color.Black) {
                DownloadReportButton(modifier = Modifier.padding(16.dp))
            }
        },
        containerColor = Color.Black
    ) { paddingValues ->
        report?.let {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(horizontal = 16.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Spacer(modifier = Modifier.height(0.dp))
                ScoreHeader(it.totalScore, it.scoreRating, it.geminiFeedback)
                MetricsCard(it.performanceMetrics)
                EventLogCard(it.events)
                Spacer(modifier = Modifier.height(16.dp))
            }
        } ?: Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
    }
}
