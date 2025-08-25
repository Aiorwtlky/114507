package com.example.mdgapp.data.model

import java.time.LocalDateTime

/**
 * 表示一個可下載的行車紀錄器影像檔案。
 *
 * @param id 檔案的唯一識別碼。
 * @param fileName 檔案名稱，通常包含時間資訊。
 * @param downloadUrl 用於下載的直接 URL。
 * @param fileSize 檔案大小（以位元組為單位）。
 * @param timestamp 影像錄製的精確時間點。
 */
data class VideoFile(
    val id: String,
    val fileName: String,
    val downloadUrl: String,
    val fileSize: Long,
    val timestamp: LocalDateTime
)
