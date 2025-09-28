package com.example.mdgapp.ui.screen

import android.widget.Toast
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.GroupManagementViewModel
import com.example.mdgapp.data.viewmodel.GroupMember

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GroupManagementScreen(
    navController: NavController,
    viewModel: GroupManagementViewModel = viewModel(),
    // 新增 isManager 參數，用於區分權限
    isManager: Boolean
) {
    val groupInfo by viewModel.groupInfo.collectAsState()
    val members by viewModel.members.collectAsState()
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(groupInfo.groupName) },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回")
                    }
                },
                actions = {
                    // 只有管理者才能看到設定按鈕
                    if (isManager) {
                        IconButton(onClick = { navController.navigate("groupSettings") }) {
                            Icon(Icons.Default.Settings, "群組設定")
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Black,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White,
                    actionIconContentColor = Color.White
                )
            )
        },
        floatingActionButton = {
            // 只有管理者才能看到新增成員按鈕
            if (isManager) {
                FloatingActionButton(
                    onClick = { navController.navigate("addMember") },
                    containerColor = Color.White
                ) {
                    Icon(Icons.Default.Add, "新增成員", tint = Color.Black)
                }
            }
        },
        containerColor = Color.Black
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier.padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Text("團隊成員 (${members.size})", style = MaterialTheme.typography.titleMedium, color = Color.White)
            }
            items(members, key = { it.id }) { member ->
                MemberCard(
                    member = member,
                    onClick = {
                        // 所有使用者都可以查看成員詳情
                        navController.navigate("memberDetail/${member.id}")
                    },
                    // 只有管理者才能看到管理員專屬的下拉選單
                    isManager = isManager,
                    onViewReportClick = {
                        // 導航到管理者查看該成員報表的路由
                        navController.navigate("managerReportDateList/${member.id}")
                    },
                    onViewVideoClick = {
                        // 導航到管理者查看該成員影片的路由
                        navController.navigate("managerDownloadFileList/${member.id}")
                    },
                    onRemoveMemberClick = {
                        viewModel.removeMember(member)
                        Toast.makeText(context, "已移除 ${member.name}", Toast.LENGTH_SHORT).show()
                    }
                )
            }
        }
    }
}

@Composable
fun MemberCard(
    member: GroupMember,
    onClick: () -> Unit,
    isManager: Boolean,
    onViewReportClick: () -> Unit,
    onViewVideoClick: () -> Unit,
    onRemoveMemberClick: () -> Unit
) {
    var showMenu by remember { mutableStateOf(false) }

    Card(
        onClick = onClick,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Image(
                painter = painterResource(id = member.avatarResId),
                contentDescription = member.name,
                modifier = Modifier.size(48.dp).clip(CircleShape)
            )
            Spacer(Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(member.name, color = Color.White, fontWeight = FontWeight.Bold)
                Text(member.status, color = if (member.status == "在線") Color.Green else Color.Gray)
            }

            // 只有管理者才能看到更多選項的按鈕
            if (isManager) {
                Box {
                    IconButton(onClick = { showMenu = true }) {
                        Icon(Icons.Default.MoreVert, "更多選項", tint = Color.White)
                    }
                    DropdownMenu(
                        expanded = showMenu,
                        onDismissRequest = { showMenu = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("查看報表") },
                            onClick = {
                                onViewReportClick()
                                showMenu = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("查看行車影像") },
                            onClick = {
                                onViewVideoClick()
                                showMenu = false
                            }
                        )
                        DropdownMenuItem(
                            text = { Text("移除成員", color = Color.Red) },
                            onClick = {
                                onRemoveMemberClick()
                                showMenu = false
                            }
                        )
                    }
                }
            }
        }
    }
}