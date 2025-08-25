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

    // 持有所有日期的日誌列表
    private val _dailyLogs = MutableStateFlow<List<DailyVideoLog>>(emptyList())
    val dailyLogs: StateFlow<List<DailyVideoLog>> = _dailyLogs.asStateFlow()

    // 只持有當前被選中日期的日誌
    private val _selectedDateLog = MutableStateFlow<DailyVideoLog?>(null)
    val selectedDateLog: StateFlow<DailyVideoLog?> = _selectedDateLog.asStateFlow()

    init {
        fetchVideoLogs()
    }

    /**
     * 當使用者從主列表點擊某個日期時，更新 _selectedDateLog 的狀態。
     */
    fun selectDate(date: LocalDate) {
        val logForDate = _dailyLogs.value.find { it.date == date }
        _selectedDateLog.value = logForDate
    }

    private fun fetchVideoLogs() {
        viewModelScope.launch {
            val today = LocalDate.now()
            val logs = (0..6).map { dayIndex ->
                val date = today.minusDays(dayIndex.toLong())
                DailyVideoLog(
                    date = date,
                    videos = generateMockVideoFilesForDate(date)
                )
            }
            _dailyLogs.value = logs
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

    private fun generateMockVideoFilesForDate(date: LocalDate): List<VideoFile> {
        val formatter = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")
        return (1..Random.nextInt(5, 15)).map {
            val randomHour = Random.nextInt(0, 24)
            val randomMinute = Random.nextInt(0, 60)
            val randomSecond = Random.nextInt(0, 60)
            val timestamp = date.atTime(randomHour, randomMinute, randomSecond)
            val fileName = "VID_${timestamp.format(formatter)}.mp4"

            VideoFile(
                id = "${date}_$it",
                fileName = fileName,
                downloadUrl = "https://example.com/videos/$fileName",
                fileSize = Random.nextLong(50_000_000, 300_000_000),
                timestamp = timestamp
            )
        }.sortedBy { it.timestamp }
    }
}
