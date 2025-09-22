package com.example.mdgapp.data.viewmodel

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

// 這是專為駕駛員設計的 ViewModel，邏輯與您最初的版本完全相同
class DriverDownloadViewModel : ViewModel() {

    private val _dailyLogs = MutableStateFlow<List<DailyVideoLog>>(emptyList())
    val dailyLogs: StateFlow<List<DailyVideoLog>> = _dailyLogs.asStateFlow()

    private val _selectedDateLog = MutableStateFlow<DailyVideoLog?>(null)
    val selectedDateLog: StateFlow<DailyVideoLog?> = _selectedDateLog.asStateFlow()

    init {
        // 只載入單一駕駛員的影片紀錄
        fetchVideoLogsForCurrentUser()
    }

    fun selectDate(date: LocalDate) {
        _selectedDateLog.value = _dailyLogs.value.find { it.date == date }
    }

    private fun fetchVideoLogsForCurrentUser() {
        viewModelScope.launch {
            val today = LocalDate.now()
            _dailyLogs.value = (0..2).map { dayIndex ->
                val date = today.minusDays(dayIndex.toLong())
                DailyVideoLog(
                    date = date,
                    videos = generateSegmentedVideoFilesForDate(date)
                )
            }
        }
    }

    private fun generateSegmentedVideoFilesForDate(date: LocalDate): List<VideoFile> {
        val formatter = DateTimeFormatter.ofPattern("yyyyMMdd_HH'h'")
        return (0..7).map { segmentIndex ->
            val startHour = segmentIndex * 3
            val timestamp = date.atTime(startHour, 0)
            val fileName = "VID_${timestamp.format(formatter)}.mp4"

            VideoFile(
                id = "${date}_$segmentIndex",
                fileName = fileName,
                downloadUrl = "https://example.com/videos/$fileName",
                fileSize = Random.nextLong(800_000_000, 2_500_000_000),
                timestamp = timestamp
            )
        }
    }
    // 您原有的 startDownload 函式可以按需加回此處
}