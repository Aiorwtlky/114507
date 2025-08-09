package com.example.mdgapp.ui.component

import android.graphics.Color as GColor
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.components.Description
import com.github.mikephil.charting.data.*
import com.github.mikephil.charting.formatter.IndexAxisValueFormatter
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet

@Composable
fun RouteMapLineChartBox(
    modifier: Modifier = Modifier
) {
    val entries = listOf(
        Entry(0f, 3.0f),
        Entry(1f, 5.2f),
        Entry(2f, 3.8f),
        Entry(3f, 4.5f),
        Entry(4f, 4.0f),
        Entry(5f, 5.5f)
    )
    val labels = listOf("1 km", "2 km", "3 km", "4 km", "5 km", "6 km")

    AndroidView(factory = { context ->
        LineChart(context).apply {
            // 設定資料
            val dataSet = LineDataSet(entries, "速度").apply {
                color = GColor.CYAN
                valueTextColor = GColor.TRANSPARENT
                lineWidth = 2f
                setDrawCircles(true)
                circleRadius = 4f
                setCircleColor(GColor.CYAN)
                setDrawValues(false)
                mode = LineDataSet.Mode.CUBIC_BEZIER // 曲線效果
            }

            data = LineData(dataSet as ILineDataSet)

            // X軸設定
            xAxis.apply {
                position = XAxis.XAxisPosition.BOTTOM
                valueFormatter = IndexAxisValueFormatter(labels)
                granularity = 1f
                textColor = GColor.DKGRAY
                setDrawGridLines(false)
            }

            // Y軸設定
            axisLeft.textColor = GColor.DKGRAY
            axisRight.isEnabled = false

            // 圖例與描述
            legend.isEnabled = false
            description = Description().apply { text = "" }

            setTouchEnabled(false)
            setScaleEnabled(false)
        }
    }, modifier = modifier)
}
