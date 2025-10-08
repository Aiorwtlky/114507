package com.example.mdgapp.ui.screen

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.data.viewmodel.GroupManagementViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddMemberScreen(
    navController: NavController,
    viewModel: GroupManagementViewModel = viewModel()
) {
    val groupInfo by viewModel.groupInfo.collectAsState()
    val inviteLink = "https://my-driving-god.com/join?group=${groupInfo.groupName.replace(" ", "")}"

    Scaffold(
        topBar = {
            TopAppBar(
                // ✅ 修正：補上 title 參數
                title = { Text("新增成員") },
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
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text("邀請成員加入 ${groupInfo.groupName}", color = Color.White, fontSize = 22.sp)
            Spacer(Modifier.height(32.dp))
            Image(painter = painterResource(id = R.drawable.ic_qr), contentDescription = "QR Code", modifier = Modifier.size(200.dp))
            Spacer(Modifier.height(16.dp))
            Text("請成員掃描 QR Code 或點擊以下連結加入", color = Color.Gray, textAlign = TextAlign.Center)
            Spacer(Modifier.height(16.dp))
            Text(inviteLink, color = Color.Cyan, textAlign = TextAlign.Center)
        }
    }
}