package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CreditCard
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.NfcViewModel
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.ui.theme.iOsBackground
import com.example.mdgapp.ui.theme.iOsBlue
import com.example.mdgapp.ui.theme.iOsComponentBackground
import com.example.mdgapp.ui.theme.iOsTextPrimary
import com.example.mdgapp.ui.theme.iOsTextSecondary

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CardCheckInScreen(
    navController: NavController,
    profileViewModel: ProfileViewModel = viewModel(),
    nfcViewModel: NfcViewModel = viewModel()
) {
    val profileUiState by profileViewModel.uiState.collectAsState()
    val nfcUiState by nfcViewModel.uiState.collectAsState()
    val userProfile = profileUiState.userProfile

    // 頁面載入時獲取使用者資料
    LaunchedEffect(Unit) {
        if (userProfile == null && !profileUiState.isLoading) {
            profileViewModel.fetchUserProfile()
        }
    }

    // 清理 NFC 狀態
    DisposableEffect(Unit) {
        onDispose {
            nfcViewModel.resetState()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("實體卡片註冊") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = iOsComponentBackground,
                    titleContentColor = iOsTextPrimary,
                    navigationIconContentColor = iOsTextPrimary
                )
            )
        },
        containerColor = iOsBackground
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentAlignment = Alignment.Center
        ) {
            when {
                profileUiState.isLoading -> {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator(color = iOsBlue)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            "正在讀取個人資料...",
                            color = iOsTextSecondary,
                            fontSize = 18.sp,
                            textAlign = TextAlign.Center
                        )
                    }
                }
                profileUiState.errorMessage != null -> {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(horizontal = 32.dp)
                    ) {
                        Text(
                            text = "資料載入失敗：\n${profileUiState.errorMessage}",
                            color = Color.Red,
                            fontSize = 18.sp,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = { profileViewModel.fetchUserProfile() },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = iOsBlue
                            )
                        ) {
                            Text("重試")
                        }
                    }
                }
                userProfile != null -> {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(horizontal = 32.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.CreditCard,
                            contentDescription = "實體卡片圖示",
                            tint = iOsBlue,
                            modifier = Modifier.size(120.dp)
                        )

                        Spacer(modifier = Modifier.height(32.dp))

                        Text(
                            "準備註冊卡片",
                            color = iOsTextPrimary,
                            fontSize = 28.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        Text(
                            "請將您的實體卡片\n靠近手機背面的 NFC 感應區",
                            color = iOsTextSecondary,
                            fontSize = 16.sp,
                            textAlign = TextAlign.Center
                        )

                        // 顯示後端綁定進度
                        if (nfcUiState.isBindingInProgress) {
                            Spacer(modifier = Modifier.height(32.dp))
                            Row(
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(20.dp),
                                    color = iOsBlue,
                                    strokeWidth = 2.dp
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "正在同步至後端...",
                                    fontSize = 14.sp,
                                    color = iOsTextSecondary
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(32.dp))

                        // 顯示當前綁定狀態
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = iOsComponentBackground
                            )
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                horizontalAlignment = Alignment.Start
                            ) {
                                Text(
                                    text = "當前綁定狀態",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = iOsTextPrimary
                                )
                                Spacer(modifier = Modifier.height(8.dp))

                                val currentUid = userProfile.personnelprofile?.nfcCardId
                                if (currentUid != null) {
                                    Text(
                                        text = "已綁定 UID: $currentUid",
                                        fontSize = 12.sp,
                                        color = iOsTextSecondary
                                    )
                                } else {
                                    Text(
                                        text = "尚未綁定任何裝置",
                                        fontSize = 12.sp,
                                        color = iOsTextSecondary
                                    )
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(32.dp))

                        Text(
                            "注意：一位使用者只能綁定一個 UID\n註冊新裝置將覆蓋原有綁定",
                            fontSize = 12.sp,
                            color = iOsTextSecondary,
                            textAlign = TextAlign.Center
                        )
                    }
                }
            }
        }
    }
}