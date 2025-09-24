package com.example.mdgapp.ui.screen

import android.graphics.Paint
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.DriverHistoryUiState
import com.example.mdgapp.data.viewmodel.DriverHistoryViewModel
import com.example.mdgapp.ui.component.HistorySection
import com.example.mdgapp.ui.component.ChartFilterMenus

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DriverHistoryScreen(
    navController: NavController,
    viewModel: DriverHistoryViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("個人歷史數據總覽") },
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
        if (uiState.isLoading && uiState.totalTrips == 0) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(16.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {
                // 核心數據卡片
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    MetricCard("總累積里程", uiState.totalMileage.toString(), "公里", Modifier.weight(1f))
                    MetricCard("總駕駛時長", uiState.totalDurationHours.toString(), "小時", Modifier.weight(1f))
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    MetricCard("總行程次數", uiState.totalTrips.toString(), "次", Modifier.weight(1f))
                    MetricCard("生涯平均分數", uiState.lifetimeAverageScore.toString(), "分", Modifier.weight(1f))
                }

                // 分數趨勢分析
                // ✅ 同樣改為呼叫新的通用 ChartFilterMenus
                HistorySection(title = "分數趨勢分析") {
                    ChartFilterMenus(
                        timeUnitOptions = uiState.timeUnitOptions,
                        selectedTimeUnit = uiState.selectedTimeUnit,
                        valueOptions = uiState.valueOptions,
                        selectedValue = uiState.selectedValue,
                        onTimeUnitSelected = { viewModel.onTimeUnitSelected(it) },
                        onValueSelected = { viewModel.onValueSelected(it) }
                    )

                    if(uiState.isLoading) {
                        Box(Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center){
                            CircularProgressIndicator()
                        }
                    } else {
                        TrendChart(
                            data = uiState.chartData,
                            labels = uiState.chartXAxisLabels,
                            modifier = Modifier.fillMaxWidth().height(200.dp).padding(top = 8.dp)
                        )
                    }
                }

                // 駕駛行為分析
                HistorySection(title = "駕駛行為分析") {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("總違規次數", color = Color.Gray, fontSize = 16.sp)
                            Text("${uiState.totalEvents} 次", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                        }
                        HorizontalDivider(color = Color(0xFF424242), modifier = Modifier.padding(vertical = 8.dp))

                        uiState.topEvents.forEach { (event, count) ->
                            EventStatRow(event, count)
                        }
                    }
                }
            }
        }
    }
}


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChartFilterMenus(
    uiState: DriverHistoryUiState,
    onTimeUnitSelected: (String) -> Unit,
    onValueSelected: (String) -> Unit
) {
    var isTimeUnitExpanded by remember { mutableStateOf(false) }
    var isValueExpanded by remember { mutableStateOf(false) }

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // ... (下拉式選單的程式碼不變)
        ExposedDropdownMenuBox(
            expanded = isTimeUnitExpanded,
            onExpandedChange = { isTimeUnitExpanded = it },
            modifier = Modifier.weight(1f)
        ) {
            OutlinedTextField(
                value = uiState.selectedTimeUnit,
                onValueChange = {},
                readOnly = true,
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = isTimeUnitExpanded) },
                modifier = Modifier.menuAnchor(),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White
                )
            )
            ExposedDropdownMenu(
                expanded = isTimeUnitExpanded,
                onDismissRequest = { isTimeUnitExpanded = false }
            ) {
                uiState.timeUnitOptions.forEach { option ->
                    DropdownMenuItem(
                        text = { Text(option) },
                        onClick = {
                            onTimeUnitSelected(option)
                            isTimeUnitExpanded = false
                        }
                    )
                }
            }
        }
        ExposedDropdownMenuBox(
            expanded = isValueExpanded,
            onExpandedChange = { isValueExpanded = it },
            modifier = Modifier.weight(1f)
        ) {
            OutlinedTextField(
                value = uiState.selectedValue,
                onValueChange = {},
                readOnly = true,
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = isValueExpanded) },
                modifier = Modifier.menuAnchor(),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White
                )
            )
            ExposedDropdownMenu(
                expanded = isValueExpanded,
                onDismissRequest = { isValueExpanded = false }
            ) {
                uiState.valueOptions.forEach { option ->
                    DropdownMenuItem(
                        text = { Text(option) },
                        onClick = {
                            onValueSelected(option)
                            isValueExpanded = false
                        }
                    )
                }
            }
        }
    }
}

// ✅ 這才是正確的 MetricCard 函式定義
@Composable
fun MetricCard(title: String, value: String, unit: String, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(title, color = Color.Gray, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.Bottom) {
                Text(value, color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.width(4.dp))
                Text(unit, color = Color.White, fontSize = 16.sp, modifier = Modifier.padding(bottom = 4.dp))
            }
        }
    }
}

@Composable
fun EventStatRow(event: String, count: Int) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(event, color = Color.White, fontSize = 16.sp)
        Text("$count 次", color = Color.Red, fontSize = 16.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
fun TrendChart(data: List<Int>, labels: List<String>, modifier: Modifier = Modifier) {
    // ... (TrendChart 的程式碼不變)
    if (data.isEmpty() || labels.isEmpty()) return
    val density = LocalDensity.current
    val textPaint = remember {
        Paint().apply {
            color = android.graphics.Color.WHITE
            textAlign = Paint.Align.CENTER
            textSize = density.run { 12.sp.toPx() }
        }
    }
    val maxValue = 100
    val minValue = 60
    Canvas(modifier = modifier.background(Color(0xFF2A2A2E))) {
        val yAxisPadding = 40.dp.toPx()
        val xAxisPadding = 30.dp.toPx()
        val chartWidth = size.width - yAxisPadding
        val chartHeight = size.height - xAxisPadding
        (0..4).forEach { i ->
            val value = minValue + (i * (maxValue - minValue) / 4)
            val y = chartHeight - (i * chartHeight / 4)
            drawContext.canvas.nativeCanvas.drawText(
                value.toString(),
                0f,
                y + textPaint.textSize / 2,
                textPaint
            )
            drawLine(
                color = Color.DarkGray,
                start = Offset(yAxisPadding, y),
                end = Offset(size.width, y),
                pathEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 10f))
            )
        }
        val points = data.mapIndexed { index, value ->
            val x = yAxisPadding + index * chartWidth / (data.size - 1).coerceAtLeast(1)
            val yValue = if (maxValue == minValue) 0.5f else (value - minValue).toFloat() / (maxValue - minValue)
            val y = chartHeight - (yValue * chartHeight)
            Offset(x, y.coerceIn(0f, chartHeight))
        }
        points.forEachIndexed { index, offset ->
            if (index < points.size - 1) {
                drawLine(
                    color = Color.Cyan,
                    start = offset,
                    end = points[index + 1],
                    strokeWidth = 5f
                )
            }
        }
        points.forEachIndexed{ index, offset ->
            drawCircle(color = Color.White, radius = 8f, center = offset)
            val labelStep = (labels.size / 7).coerceAtLeast(1)
            if (index % labelStep == 0) {
                drawContext.canvas.nativeCanvas.drawText(
                    labels.getOrElse(index) { "" },
                    offset.x,
                    size.height,
                    textPaint
                )
            }
        }
    }
}