package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.GroupManagementViewModel
import com.example.mdgapp.ui.component.HistorySection

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MemberDetailScreen(
    navController: NavController,
    memberId: String?,
    viewModel: GroupManagementViewModel = viewModel()
) {
    LaunchedEffect(memberId) {
        memberId?.let { viewModel.loadMemberDetails(it) }
    }
    val member by viewModel.selectedMemberDetail.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                // ✅ 修正：補上 title 參數，並動態顯示成員姓名
                title = { Text(member?.name ?: "成員資訊") },
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
        member?.let {
            Column(
                modifier = Modifier
                    .padding(paddingValues)
                    .padding(16.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                HistorySection(title = "成員資訊") {
                    Text("姓名: ${it.name}", color = Color.White)
                }
                HistorySection(title = "過往趨勢圖表") {
                    Box(Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
                        Text("圖表區域", color = Color.Gray)
                    }
                }
                HistorySection(title = "過往行程") {
                    Text("顯示過往行程...", color = Color.Gray)
                }
            }
        } ?: Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
    }
}