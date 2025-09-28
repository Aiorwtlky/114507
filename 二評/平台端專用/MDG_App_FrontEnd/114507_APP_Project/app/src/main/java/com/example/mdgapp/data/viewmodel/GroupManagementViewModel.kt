package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.R
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.time.LocalDate

// --- Data Models ---
data class GroupInfo(
    val groupName: String,
    val unitName: String,
    val leaderName: String
)

data class GroupMember(
    val id: String,
    val avatarResId: Int,
    val memberId: String,
    val name: String,
    val averageScore: Int,
    val joinDate: LocalDate,
    // ✅ 1. 新增 status 欄位，以符合 GroupManagementScreen 的需求
    val status: String
)

// --- ViewModel ---
class GroupManagementViewModel : ViewModel() {

    private val _groupInfo = MutableStateFlow(
        GroupInfo(groupName = "總部第一車隊", unitName = "運輸部", leaderName = "王大明")
    )
    val groupInfo: StateFlow<GroupInfo> = _groupInfo.asStateFlow()

    private val _members = MutableStateFlow<List<GroupMember>>(emptyList())
    val members: StateFlow<List<GroupMember>> = _members.asStateFlow()

    private val _currentUserIdentity = MutableStateFlow("")
    val currentUserIdentity: StateFlow<String> = _currentUserIdentity.asStateFlow()

    private val _selectedMemberDetail = MutableStateFlow<GroupMember?>(null)
    val selectedMemberDetail: StateFlow<GroupMember?> = _selectedMemberDetail.asStateFlow()

    init {
        loadGroupMembers()
        loadCurrentUser()
    }

    private fun loadGroupMembers() {
        _members.value = listOf(
            // ✅ 在建立成員時，填入 status 狀態
            GroupMember("MGR-001", R.drawable.jiboda1, "MGR-001", "陳廷軒", 92, LocalDate.of(2024, 1, 15), status = "在線"),
            GroupMember("D-007", R.drawable.mywife, "D-007", "姜諧潾", 84, LocalDate.of(2024, 3, 22), status = "離線"),
            GroupMember("D-008", R.drawable.jiboda2, "D-008", "季博達", 95, LocalDate.of(2024, 2, 10), status = "在線")
        )
    }

    private fun loadCurrentUser() {
        val manager = _members.value.first { it.id == "MGR-001" }
        _currentUserIdentity.value = "${manager.memberId} ${manager.name} (管理者)"
    }

    fun loadMemberDetails(memberId: String) {
        _selectedMemberDetail.value = _members.value.find { it.id == memberId }
    }

    fun updateGroupName(newName: String) {
        _groupInfo.update { it.copy(groupName = newName) }
    }

    // ✅ 2. 新增 removeMember 函式
    fun removeMember(memberToRemove: GroupMember) {
        _members.update { currentMembers ->
            currentMembers.filterNot { it.id == memberToRemove.id }
        }
        // TODO: 在此處呼叫後端 API 來實際從資料庫移除成員
    }
}