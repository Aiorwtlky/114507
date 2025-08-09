package com.example.mdgapp.ui.component

import android.graphics.Color as GColor
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.components.Description
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.data.*
import com.github.mikephil.charting.formatter.IndexAxisValueFormatter
import com.github.mikephil.charting.components.Legend

// ✅ 自訂時間資料類別，支援小時與分鐘
data class HourTime(val hour: Int, val minute: Int)

@Composable
fun InteractiveLineChart(
    modifier: Modifier = Modifier,
    selectedTab: String = "週",
    clockInTime: HourTime = HourTime(10, 56),
    clockOutTime: HourTime = HourTime(17, 58)
) {
    val (dataSets, xLabels) = remember(selectedTab, clockInTime, clockOutTime) {
        when (selectedTab) {
            "月" -> Pair(listOf(monthLineDataSet()), listOf("1月", "2月", "3月", "4月", "5月"))
            "週" -> Pair(listOf(weekLineDataSet()), listOf("週一", "週二", "週三", "週四", "週五"))
            "日" -> {
                val (ds, labels) = generateDayDataSet(clockInTime, clockOutTime)
                Pair(listOf(ds), labels)
            }
            else -> Pair(listOf(weekLineDataSet()), listOf("週一", "週二", "週三", "週四", "週五"))
        }
    }

    AndroidView(
        modifier = modifier,
        factory = { context ->
            LineChart(context).apply {
                setTouchEnabled(true)
                setPinchZoom(true)
                setBackgroundColor(GColor.BLACK)
                axisLeft.apply {
                    textColor = GColor.WHITE
                    gridColor = GColor.DKGRAY
                    axisMinimum = 0f
                    axisMaximum = 100f
                    labelCount = 6
                }
                axisRight.isEnabled = false
                xAxis.apply {
                    textColor = GColor.WHITE
                    gridColor = GColor.DKGRAY
                    position = XAxis.XAxisPosition.BOTTOM
                    granularity = 1f
                    setDrawGridLines(true)
                }
                legend.apply {
                    textColor = GColor.WHITE
                    form = Legend.LegendForm.LINE
                    yOffset = 16f
                }
                description = Description().apply { text = "" }
            }
        },
        update = { chart ->
            chart.data = LineData(dataSets)
            chart.xAxis.valueFormatter = IndexAxisValueFormatter(xLabels)
            chart.invalidate()
        }
    )
}

private fun roundUpToNextHour(time: HourTime): Int {
    return if (time.minute == 0) time.hour else time.hour + 1
}

private fun generateDayDataSet(
    clockIn: HourTime,
    clockOut: HourTime
): Pair<LineDataSet, List<String>> {
    val startHour = roundUpToNextHour(clockIn)
    val endHour = roundUpToNextHour(clockOut)
    val hours = endHour - startHour

    val entries = mutableListOf<Entry>()
    val labels = mutableListOf<String>()

    for (i in 0..hours) {
        val hour = startHour + i
        entries.add(Entry(i.toFloat(), (60..90).random().toFloat())) // 假分數
        labels.add(String.format("%02d:00", hour))
    }

    return Pair(LineDataSet(entries, "日行為").applyStyle(), labels)
}

// ✅ 假資料
private fun monthLineDataSet(): LineDataSet {
    val entries = listOf(
        Entry(0f, 72f), Entry(1f, 81f), Entry(2f, 75f), Entry(3f, 88f), Entry(4f, 90f)
    )
    return LineDataSet(entries, "月平均").applyStyle()
}

private fun weekLineDataSet(): LineDataSet {
    val entries = listOf(
        Entry(0f, 65f), Entry(1f, 70f), Entry(2f, 78f), Entry(3f, 80f), Entry(4f, 85f)
    )
    return LineDataSet(entries, "週平均").applyStyle()
}

private fun LineDataSet.applyStyle(): LineDataSet = apply {
    color = GColor.WHITE
    valueTextColor = GColor.WHITE
    lineWidth = 2f
    setDrawCircles(true)
    circleRadius = 4f
    setCircleColor(GColor.WHITE)
    setDrawValues(false)
}
