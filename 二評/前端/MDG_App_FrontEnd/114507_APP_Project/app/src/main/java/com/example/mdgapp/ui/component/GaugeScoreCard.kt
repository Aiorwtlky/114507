package com.example.mdgapp.ui.component

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun GaugeScoreCard(
    score: Int,
    label: String,
    modifier: Modifier = Modifier
) {
    val clampedScore = score.coerceIn(0, 100)
    val angle = 180f * clampedScore / 100f

    Box(
        modifier = modifier
            .aspectRatio(2f)
            .background(Color(0xFF1C1C1C), shape = RoundedCornerShape(16.dp))
            .padding(16.dp)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val centerX = size.width / 2
            val centerY = size.height
            val radius = size.width / 2.2f

            // 背景弧形刻度
            drawArc(
                color = Color.DarkGray,
                startAngle = 180f,
                sweepAngle = 180f,
                useCenter = false,
                topLeft = Offset(centerX - radius, centerY - radius),
                size = Size(radius * 2, radius * 2),
                style = Stroke(16f, cap = StrokeCap.Round)
            )

            // 分數進度弧
            drawArc(
                color = Color.Cyan,
                startAngle = 180f,
                sweepAngle = angle,
                useCenter = false,
                topLeft = Offset(centerX - radius, centerY - radius),
                size = Size(radius * 2, radius * 2),
                style = Stroke(16f, cap = StrokeCap.Round)
            )
        }

        // 中央文字
        Column(
            modifier = Modifier.align(Alignment.Center),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("$score", fontSize = 28.sp, color = Color.White)
            Text(label, fontSize = 14.sp, color = Color.Gray)
        }
    }
}
