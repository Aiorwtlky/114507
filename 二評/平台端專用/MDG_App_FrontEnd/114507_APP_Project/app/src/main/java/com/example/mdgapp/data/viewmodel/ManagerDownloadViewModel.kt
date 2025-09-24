package com.example.mdgapp.data.viewmodel

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.os.Environment
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.DailyVideoLog
import com.example.mdgapp.data.model.DriverInfo
import com.example.mdgapp.data.model.VideoFile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlin.random.Random

class ManagerDownloadViewModel : ViewModel() {

    private val _drivers = MutableStateFlow<List<DriverInfo>>(emptyList())
    val drivers: StateFlow<List<DriverInfo>> = _drivers.asStateFlow()

    private val _dailyLogs = MutableStateFlow<List<DailyVideoLog>>(emptyList())
    val dailyLogs: StateFlow<List<DailyVideoLog>> = _dailyLogs.asStateFlow()

    private val _selectedDateLog = MutableStateFlow<DailyVideoLog?>(null)
    val selectedDateLog: StateFlow<DailyVideoLog?> = _selectedDateLog.asStateFlow()

    private var allVideoLogs: Map<String, List<DailyVideoLog>> = emptyMap()

    init {
        loadInitialManagerData()
    }

    fun selectDate(date: LocalDate) {
        _selectedDateLog.value = _dailyLogs.value.find { it.date == date }
    }

    fun loadDailyLogsForDriver(driverId: String) {
        _dailyLogs.value = allVideoLogs[driverId] ?: emptyList()
    }

    private fun loadInitialManagerData() {
        viewModelScope.launch {
            val driverList = listOf(
                // ✅ 修正：將第四個參數從 R.drawable... (Int) 改為 null (符合 String? 類型)
                DriverInfo("D-007", "季博達", 84, avatarUrl = null),
                DriverInfo("D-008", "姜諧潾", 95, avatarUrl = null)
            )
            _drivers.value = driverList

            allVideoLogs = driverList.associate { driver ->
                val today = LocalDate.now()
                driver.driverId to (0..2).map { dayIndex ->
                    val date = today.minusDays(dayIndex.toLong())
                    DailyVideoLog(
                        date = date,
                        videos = generateSegmentedVideoFilesForDate(date, driver.driverName)
                    )
                }
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

    private fun generateSegmentedVideoFilesForDate(date: LocalDate, driverName: String): List<VideoFile> {
        val formatter = DateTimeFormatter.ofPattern("yyyyMMdd_HH'h'")
        return (0..7).map { segmentIndex ->
            val startHour = segmentIndex * 3
            val timestamp = date.atTime(startHour, 0)
            val fileName = "VID_${driverName}_${timestamp.format(formatter)}.mp4"

            VideoFile(
                id = "${date}_$segmentIndex",
                fileName = fileName,
                downloadUrl = "https://example.com/videos/$fileName",
                fileSize = Random.nextLong(800_000_000, 2_500_000_000),
                timestamp = timestamp
            )
        }
    }
}