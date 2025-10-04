// 檔案路徑: app/src/main/java/com/example/mdgapp/data/model/TripMapper.kt

package com.example.mdgapp.data.model

import com.example.mdgapp.data.viewmodel.LastTripInfo
import com.example.mdgapp.data.viewmodel.Violation
import java.time.Duration
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

// 這是一個擴充函式，可以讓我們像這樣呼叫：val lastTripInfo = trip.toLastTripInfo()
fun Trip.toLastTripInfo(): LastTripInfo {
    val formatter = DateTimeFormatter.ISO_OFFSET_DATE_TIME
    val start = LocalDateTime.parse(this.startTime, formatter)
    val end = this.endTime?.let { LocalDateTime.parse(it, formatter) }

    return LastTripInfo(
        startTime = start,
        endTime = end ?: start, // 如果結束時間為 null，暫時用開始時間代替
        duration = if (end != null) Duration.between(start, end) else Duration.ZERO,
        startLocation = "來源地資訊待補", // TODO: 需從 Trip Detail API 獲取
        endLocation = "目的地資訊待補", // TODO: 需從 Trip Detail API 獲取
        mileage = 0.0, // TODO: 需從 Trip Detail API 獲取
        totalScore = this.score.toDoubleOrNull()?.toInt() ?: 0,
        improvementPercentage = 0, // TODO: 需要有比較的基準才能計算
        violations = listOf(
            Violation("違規項目待補", 0) // TODO: 需從 Trip Detail API 獲取
        ),
        aiSuggestion = "AI 建議待補" // TODO: 需從 Trip Detail API 獲取
    )
}

fun DrivingReport.toLastTripInfo(): LastTripInfo {
    // 假設時間格式是 "HH:mm"，並結合報告的日期來建立完整的時間
    val startTime = this.date.atTime(java.time.LocalTime.parse(this.tripInfo.startTime))
    val endTime = this.date.atTime(java.time.LocalTime.parse(this.tripInfo.endTime))

    // 將 DrivingReport 中的 events 轉換成 Violations
    val violations = this.events.map { event ->
        com.example.mdgapp.data.viewmodel.Violation(
            item = event.eventType,
            scoreDeduction = event.deductionPoints
        )
    }

    return com.example.mdgapp.data.viewmodel.LastTripInfo(
        startTime = startTime,
        endTime = endTime,
        duration = java.time.Duration.ofMinutes(this.tripInfo.totalDurationMinutes.toLong()),
        // ✅ 修正：從傳入的 report 物件中讀取真實地點
        startLocation = this.startLocation,
        endLocation = this.endLocation,
        mileage = this.tripInfo.totalDistanceKm,
        totalScore = this.totalScore,
        improvementPercentage = this.comparisonWithAverage,
        violations = violations,
        aiSuggestion = this.geminiFeedback
    )
}