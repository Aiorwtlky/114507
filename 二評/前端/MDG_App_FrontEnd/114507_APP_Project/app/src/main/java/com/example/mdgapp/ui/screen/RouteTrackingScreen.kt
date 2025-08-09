package com.example.mdgapp.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.material3.BottomSheetScaffold
import androidx.compose.material3.rememberBottomSheetScaffoldState
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.mdgapp.ui.component.RouteMap
import com.example.mdgapp.ui.component.RouteMapLineChartBox
import com.example.mdgapp.ui.component.InfoCard
import com.example.mdgapp.util.formatHoursDecimal
import com.example.mdgapp.ui.component.InfoCardText
import com.example.mdgapp.util.formatHoursDecimal
import com.example.mdgapp.util.formatTime
import kotlinx.coroutines.launch
import androidx.compose.ui.Alignment

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RouteTrackingScreen(
    totalDistance: Float,
    time: Int,
    modifier: Modifier = Modifier
) {
    val scaffoldState = rememberBottomSheetScaffoldState()
    val coroutineScope = rememberCoroutineScope()

    BottomSheetScaffold(
        scaffoldState = scaffoldState,
        sheetPeekHeight = 180.dp,
        sheetContent = {
            // 底部統計資訊卡片區塊
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1C1C1E))
                    .padding(16.dp)
            ) {
                Text("統計資訊", fontSize = 20.sp, color = Color.White)

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    InfoCardText(
                        valueText = formatHoursDecimal(time),   // 例如 1.5 hr
                        label = "行車時長",
                        fillColor = Color(0xFF2196F3),
                        backgroundColor = Color(0x552196F3),
                        progressValue = time / 3600f,  // 秒 → 小時
                        maxProgress = 8f,
                        modifier = Modifier.weight(1f)
                    )
                    InfoCardText(
                        valueText = String.format("%.2f km", totalDistance),
                        label = "公里數",
                        fillColor = Color(0xFFF48FB1),
                        backgroundColor = Color(0x55F48FB1),
                        progressValue = totalDistance,
                        maxProgress = 100f,
                        modifier = Modifier.weight(1f)
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                RouteMapLineChartBox(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(160.dp)
                )
            }
        },
        containerColor = Color.Transparent
    ) { paddingValues ->
        // 背景地圖佔滿畫面
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(Color.Black)
        ) {
            RouteMap(modifier = Modifier.fillMaxSize())
        }
    }
}
