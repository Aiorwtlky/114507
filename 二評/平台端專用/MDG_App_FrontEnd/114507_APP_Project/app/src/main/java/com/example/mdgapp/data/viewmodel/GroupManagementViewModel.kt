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
    val joinDate: LocalDate
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
            GroupMember("MGR-001", R.drawable.jiboda1, "MGR-001", "陳廷軒", 92, LocalDate.of(2024, 1, 15)),
            GroupMember("D-007", R.drawable.mywife, "D-007", "姜諧潾", 84, LocalDate.of(2024, 3, 22)),
            GroupMember("D-008", R.drawable.jiboda2, "D-008", "季博達", 95, LocalDate.of(2024, 2, 10))
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
}