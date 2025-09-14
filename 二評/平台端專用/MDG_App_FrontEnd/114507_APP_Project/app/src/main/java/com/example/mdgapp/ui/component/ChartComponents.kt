package com.example.mdgapp.ui.component

import android.graphics.Paint
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// 這是我們在 DriverHistoryScreen 中建立的圖表元件
@Composable
fun TrendChart(data: List<Int>, labels: List<String>, modifier: Modifier = Modifier) {
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

        // 繪製Y軸 (縱軸) 標籤與背景虛線
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

        // 繪製分數折線和X軸 (橫軸) 標籤
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