package com.example.mdgapp.ui.screen

import android.widget.Toast
// ✅ 修正：新增 BorderStroke 的 import
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.GroupManagementViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GroupSettingsScreen(
    navController: NavController,
    viewModel: GroupManagementViewModel = viewModel()
) {
    val groupInfo by viewModel.groupInfo.collectAsState()
    var groupName by remember(groupInfo.groupName) { mutableStateOf(groupInfo.groupName) }
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                // ✅ 修正：補上 title 參數
                title = { Text("群組設定") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回")
                    }
                },
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
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedTextField(value = groupName, onValueChange = { groupName = it }, label = { Text("群組名稱") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = groupInfo.unitName, onValueChange = {}, label = { Text("所屬單位") }, modifier = Modifier.fillMaxWidth(), readOnly = true)

            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("組長: ${groupInfo.leaderName}", color = Color.White, modifier = Modifier.weight(1f))
                IconButton(onClick = { /* TODO: 實作新增組長邏輯 */ }) { Icon(Icons.Default.Add, "新增組長", tint = Color.White) }
                IconButton(onClick = { /* TODO: 實作移除組長邏輯 */ }) { Icon(Icons.Default.Remove, "移除組長", tint = Color.White) }
            }

            Spacer(Modifier.weight(1f))

            Button(
                onClick = {
                    viewModel.updateGroupName(groupName)
                    Toast.makeText(context, "已儲存", Toast.LENGTH_SHORT).show()
                    navController.navigateUp()
                },
                modifier = Modifier.fillMaxWidth()
            ) { Text("儲存變更") }

            OutlinedButton(
                onClick = { /* TODO: 實作刪除群組邏輯 */ },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = Color.Red),
                // ✅ 修正：將 borderColor 改為 border
                border = BorderStroke(1.dp, Color.Red)
            ) { Text("刪除群組") }
        }
    }
}