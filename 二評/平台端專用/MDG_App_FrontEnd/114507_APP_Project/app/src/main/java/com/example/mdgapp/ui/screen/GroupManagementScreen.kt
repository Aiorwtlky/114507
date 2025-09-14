package com.example.mdgapp.ui.screen

import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.GroupManagementViewModel
import com.example.mdgapp.data.viewmodel.GroupMember
import com.example.mdgapp.ui.component.HistorySection
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GroupManagementScreen(
    navController: NavController,
    viewModel: GroupManagementViewModel = viewModel()
) {
    val groupInfo by viewModel.groupInfo.collectAsState()
    val members by viewModel.members.collectAsState()
    val currentUserIdentity by viewModel.currentUserIdentity.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("群組管理") },
                navigationIcon = { IconButton(onClick = { navController.navigateUp() }) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回")
                }},
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Black,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        },
        containerColor = Color.Black
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .padding(16.dp)
                .fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // 區塊一：群組設定
            HistorySection(title = "群組設定") {
                Column(modifier = Modifier.clickable { navController.navigate("groupSettings") }) {
                    InfoRow("目前群組", groupInfo.groupName)
                    InfoRow("所屬單位", groupInfo.unitName)
                    InfoRow("群組組長", groupInfo.leaderName)
                }
            }

            // 區塊二：組內身分
            HistorySection(title = "組內身分") {
                Text(currentUserIdentity, color = Color.White, fontSize = 14.sp)
            }

            // ✅ 區塊三：恢復成沒有 weight 的版本
            HistorySection(title = "群組成員") {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    TextButton(onClick = { navController.navigate("addMember") }) {
                        Icon(Icons.Default.Add, contentDescription = "新增成員")
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("新增成員")
                    }
                }
                // ✅ 恢復固定高度的 LazyColumn
                LazyColumn(
                    modifier = Modifier.heightIn(max = 400.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(members, key = { it.id }) { member ->
                        GroupMemberListItem(member = member, onClick = {
                            navController.navigate("memberDetail/${member.id}")
                        })
                    }
                }
            }
        }
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, color = Color.Gray, fontSize = 14.sp)
        Text(value, color = Color.White, fontSize = 14.sp)
    }
}

@Composable
fun GroupMemberListItem(member: GroupMember, onClick: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick).padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Image(
            painter = painterResource(id = member.avatarResId),
            contentDescription = "成員頭像",
            modifier = Modifier.size(48.dp).clip(CircleShape)
        )
        Spacer(modifier = Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(member.name, color = Color.White, fontWeight = FontWeight.Bold)
            Text("編號: ${member.memberId}", color = Color.Gray, fontSize = 12.sp)
            Text("加入日期: ${member.joinDate.format(DateTimeFormatter.ISO_LOCAL_DATE)}", color = Color.Gray, fontSize = 12.sp)
        }
        Text("${member.averageScore}分", color = Color.Cyan, fontSize = 16.sp)
        Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, contentDescription = "查看詳情", tint = Color.Gray)
    }
}