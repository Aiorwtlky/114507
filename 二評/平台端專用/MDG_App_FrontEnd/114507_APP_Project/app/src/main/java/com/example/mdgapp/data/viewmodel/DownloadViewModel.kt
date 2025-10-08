package com.example.mdgapp.data.viewmodel

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.os.Environment
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.DailyVideoLog
import com.example.mdgapp.data.model.VideoFile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlin.random.Random

class DownloadViewModel : ViewModel() {

    private val _dailyLogs = MutableStateFlow<List<DailyVideoLog>>(emptyList())
    val dailyLogs: StateFlow<List<DailyVideoLog>> = _dailyLogs.asStateFlow()

    private val _selectedDateLog = MutableStateFlow<DailyVideoLog?>(null)
    val selectedDateLog: StateFlow<DailyVideoLog?> = _selectedDateLog.asStateFlow()

    init {
        fetchVideoLogs()
    }

    fun selectDate(date: LocalDate) {
        _selectedDateLog.value = _dailyLogs.value.find { it.date == date }
    }

    private fun fetchVideoLogs() {
        viewModelScope.launch {
            val today = LocalDate.now()
            // --- ✅ 修改點：改為模擬 3 天的資料 ---
            _dailyLogs.value = (0..2).map { dayIndex ->
                val date = today.minusDays(dayIndex.toLong())
                DailyVideoLog(
                    date = date,
                    videos = generateSegmentedVideoFilesForDate(date)
                )
            }
        }
    }

    fun startDownload(context: Context, videoFile: VideoFile) {
        val request = DownloadManager.Request(Uri.parse(videoFile.downloadUrl))
            .setTitle(videoFile.fileName)
            .setDescription("正在下載行車紀錄...")
            .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            .setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, videoFile.fileName)
            .setAllowedOverMetered(true)
            .setAllowedOverRoaming(true)

        val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
        downloadManager.enqueue(request)
    }

    // --- ✅ 修改點：重寫模擬資料生成邏輯 ---
    private fun generateSegmentedVideoFilesForDate(date: LocalDate): List<VideoFile> {
        val formatter = DateTimeFormatter.ofPattern("yyyyMMdd_HH'h'")
        // 一天 24 小時，每 3 小時一段，共 8 個檔案
        return (0..7).map { segmentIndex ->
            val startHour = segmentIndex * 3
            val timestamp = date.atTime(startHour, 0) // 時間設定為區段的開始時間
            val fileName = "VID_${timestamp.format(formatter)}.mp4"

            VideoFile(
                id = "${date}_$segmentIndex",
                fileName = fileName,
                downloadUrl = "https://example.com/videos/$fileName", // 假的下載連結
                fileSize = Random.nextLong(800_000_000, 2_500_000_000), // 模擬 800MB - 2.5GB
                timestamp = timestamp
            )
        }
    }
}
