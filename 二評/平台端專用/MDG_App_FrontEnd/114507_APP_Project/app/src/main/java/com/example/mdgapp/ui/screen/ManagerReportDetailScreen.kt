package com.example.mdgapp.ui.screen
/*
import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Download
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ManagerReportViewModel
import com.example.mdgapp.ui.component.*
import java.time.LocalDate

// 新增檔案：管理者報表第三頁 - 報表詳情
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerReportDetailScreen(
    navController: NavController,
    dateString: String?,
    viewModel: ManagerReportViewModel // 使用 ManagerReportViewModel
) {
    val selectedDate = remember(dateString) { dateString?.let { LocalDate.parse(it) } }

    LaunchedEffect(selectedDate) {
        selectedDate?.let { viewModel.selectReportByDate(it) }
    }

    val report by viewModel.selectedReportDetail.collectAsState()
    val driver by viewModel.drivers.collectAsState() // 取得駕駛資訊
    val context = LocalContext.current

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
                // 重用 DownloadReportButton，但點擊邏輯不同
                Button(
                    onClick = {
                        val currentDriver = driver.firstOrNull() // 簡單示例，實際應傳遞 driverId
                        if (report != null && currentDriver != null) {
                            val msg = viewModel.downloadReportForDriver(report!!, currentDriver)
                            Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
                        }
                    },
                    modifier = Modifier.padding(16.dp).fillMaxWidth().height(50.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White)
                ) {
                    Icon(Icons.Default.Download, "下載圖示", tint = Color.Black)
                    Spacer(Modifier.width(8.dp))
                    Text("下載 PDF 報表", color = Color.Black)
                }
            }
        },
        containerColor = Color.Black
    ) { paddingValues ->
        // 內容部分與原 ReportDetailScreen 完全相同，可以直接重用元件
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
}*/