package com.example.mdgapp.ui.component

import androidx.compose.foundation.Canvas
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.roundToInt

@Composable
fun TrendChart(
    data: List<Int>,
    // ✅ 步驟 1.1: 新增 labels 參數，用來接收 X 軸的標籤
    labels: List<String>,
    modifier: Modifier = Modifier,
    yAxisLabelColor: Color = Color.Gray,
    gridLineColor: Color = Color.Gray.copy(alpha = 0.3f),
    lineColor: Color = Color.Cyan
) {
    if (data.isEmpty()) return

    val density = LocalDensity.current
    val textPaint = remember {
        android.graphics.Paint().apply {
            color = yAxisLabelColor.hashCode()
            textSize = with(density) { 12.sp.toPx() }
            textAlign = android.graphics.Paint.Align.CENTER
        }
    }
    val yAxisPaint = remember(textPaint) {
        android.graphics.Paint(textPaint).apply {
            textAlign = android.graphics.Paint.Align.RIGHT
        }
    }


    Canvas(modifier = modifier) {
        val yAxisPadding = 40.dp.toPx()
        val xAxisPadding = 30.dp.toPx() // 增加底部 padding 給 X 軸標籤
        val chartWidth = size.width - yAxisPadding
        val chartHeight = size.height - xAxisPadding

        val dataMin = 60
        val dataMax = 100
        val dataRange = (dataMax - dataMin).toFloat()

        // 繪製 Y 軸刻度與格線 (程式碼不變)
        val yGridLineCount = 5
        (0 until yGridLineCount).forEach { i ->
            val y = chartHeight - (i * chartHeight / (yGridLineCount - 1))
            val labelValue = dataMin + (i * dataRange / (yGridLineCount - 1))
            drawLine(
                color = gridLineColor,
                start = Offset(yAxisPadding, y),
                end = Offset(size.width, y),
                strokeWidth = 1.dp.toPx()
            )
            drawContext.canvas.nativeCanvas.drawText(
                "${labelValue.roundToInt()}",
                yAxisPadding - 8.dp.toPx(),
                y + 4.dp.toPx(),
                yAxisPaint
            )
        }

        val path = Path()
        val points = data.mapIndexed { index, value ->
            val x = yAxisPadding + (index.toFloat() / (data.size - 1).coerceAtLeast(1)) * chartWidth
            val y = chartHeight - ((value.toFloat() - dataMin) / dataRange) * chartHeight
            Offset(x, y)
        }

        points.forEachIndexed { index, offset ->
            if (index == 0) {
                path.moveTo(offset.x, offset.y)
            } else {
                path.lineTo(offset.x, offset.y)
            }
        }

        // ✅ 步驟 1.2: 繪製 X 軸標籤，且每 3 個單位顯示一個
        labels.forEachIndexed { index, label ->
            if (index % 3 == 0) { // 每 3 個單位為一區間
                drawContext.canvas.nativeCanvas.drawText(
                    label,
                    points[index].x,
                    size.height - 5.dp.toPx(), // 標籤繪製位置
                    textPaint
                )
            }
        }

        // 繪製數據線條 (程式碼不變)
        drawPath(
            path = path,
            color = lineColor,
            style = Stroke(width = 2.dp.toPx())
        )
    }
}