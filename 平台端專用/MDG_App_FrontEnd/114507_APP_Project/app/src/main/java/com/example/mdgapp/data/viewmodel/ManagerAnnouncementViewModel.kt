package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate

// 公告的資料模型
data class Announcement(
    val id: Int,
    val subject: String,
    val content: String,
    val publishDate: LocalDate,
    val publisherName: String = "王大明 (管理者)",
    val groupName: String = "總部車隊"
)

// 新增/編輯公告畫面的狀態
data class NewAnnouncementState(
    val announcementId: Int? = null,
    val subject: String = "",
    val content: String = "",
    val isScheduled: Boolean = false,
    val scheduledDate: LocalDate = LocalDate.now()
)

class ManagerAnnouncementViewModel : ViewModel() {

    private val _announcements = MutableStateFlow<List<Announcement>>(emptyList())
    val announcements: StateFlow<List<Announcement>> = _announcements.asStateFlow()

    private val _newAnnouncementState = MutableStateFlow(NewAnnouncementState())
    // ✅ 修正：移除多餘的角括號 ">"
    val newAnnouncementState: StateFlow<NewAnnouncementState> = _newAnnouncementState.asStateFlow()

    init {
        loadAnnouncements()
    }

    private fun loadAnnouncements() {
        _announcements.value = listOf(
            Announcement(1, "系統維護通知", "親愛的團隊成員，\n\n為提升系統效能，我們將於下週一 (09/22) 凌晨 02:00 至 04:00 進行系統維護，屆時 App 可能暫時無法使用，敬請見諒。", LocalDate.of(2025, 9, 14)),
            Announcement(2, "駕駛安全獎勵辦法", "為鼓勵優良駕駛，本季平均分數達95分以上同仁，將可獲得5000元獎金。", LocalDate.of(2025, 9, 1))
        )
    }

    // --- 事件處理 ---

    fun onSubjectChange(subject: String) {
        _newAnnouncementState.update { it.copy(subject = subject) }
    }

    fun onContentChange(content: String) {
        _newAnnouncementState.update { it.copy(content = content) }
    }

    fun onPublishOptionChange(isScheduled: Boolean) {
        _newAnnouncementState.update { it.copy(isScheduled = isScheduled) }
    }

    fun onDateSelected(date: LocalDate) {
        _newAnnouncementState.update { it.copy(scheduledDate = date) }
    }

    fun loadAnnouncementForEditing(id: Int) {
        val announcement = _announcements.value.find { it.id == id }
        announcement?.let {
            _newAnnouncementState.value = NewAnnouncementState(
                announcementId = it.id,
                subject = it.subject,
                content = it.content,
                isScheduled = it.publishDate.isAfter(LocalDate.now()),
                scheduledDate = it.publishDate
            )
        }
    }

    fun updateAnnouncement() {
        viewModelScope.launch {
            val updatedState = _newAnnouncementState.value
            val idToUpdate = updatedState.announcementId ?: return@launch

            val updatedAnnouncement = Announcement(
                id = idToUpdate,
                subject = updatedState.subject,
                content = updatedState.content,
                publishDate = if (updatedState.isScheduled) updatedState.scheduledDate else LocalDate.now()
            )

            _announcements.update { currentList ->
                currentList.map { if (it.id == idToUpdate) updatedAnnouncement else it }
            }
            resetNewAnnouncementState()
        }
    }

    fun publishAnnouncement() {
        viewModelScope.launch {
            val newAnnouncementData = _newAnnouncementState.value
            val newId = (_announcements.value.maxOfOrNull { it.id } ?: 0) + 1

            val announcementToAdd = Announcement(
                id = newId,
                subject = newAnnouncementData.subject,
                content = newAnnouncementData.content,
                publishDate = if (newAnnouncementData.isScheduled) newAnnouncementData.scheduledDate else LocalDate.now()
            )

            _announcements.update { listOf(announcementToAdd) + it }
            resetNewAnnouncementState()
        }
    }

    fun resetNewAnnouncementState() {
        _newAnnouncementState.value = NewAnnouncementState()
    }
}