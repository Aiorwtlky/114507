package com.example.mdgapp.data.model

import java.time.LocalDate

/**
 * 代表一整天的行車紀錄日誌。
 *
 * @param date 日期。
 * @param videos 當天錄製的所有影像檔案列表。
 */
data class DailyVideoLog(
    val date: LocalDate,
    val videos: List<VideoFile>
)
