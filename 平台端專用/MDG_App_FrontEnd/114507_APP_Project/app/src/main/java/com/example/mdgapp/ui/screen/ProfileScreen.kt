package com.example.mdgapp.ui.screen

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.local.TokenManager
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.ui.component.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    navController: NavController,
    viewModel: ProfileViewModel = viewModel()
) {
    // ⭐ 1. 訂閱整個 UiState，而不是單一的 userProfile
    val uiState by viewModel.uiState.collectAsState()
    val userProfile = uiState.userProfile
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("個人帳號管理") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(imageVector = Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
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
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when {
                // ⭐ 2. 根據 UiState 顯示不同內容
                uiState.isLoading -> {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }
                uiState.errorMessage != null -> {
                    Text(
                        text = uiState.errorMessage ?: "發生錯誤",
                        color = Color.White,
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                userProfile != null -> {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(horizontal = 16.dp)
                            .verticalScroll(rememberScrollState())
                    ) {
                        // ⭐ 3. 更新資料來源
                        ProfileHeader(
                            name = "${userProfile.lastName}${userProfile.firstName}",
                            employeeId = userProfile.personnelprofile?.personnelNumber ?: "N/A"
                        )

                        ProfileSection(title = "車輛與群組") {
                            InfoRow(label = "目前駕駛車輛", value = "MDG-0000") // API 暫無此資料
                            HorizontalDivider(color = Color(0xFF424242))
                            InfoRow(label = "所屬群組", value = "總部第一車隊") // API 暫無此資料
                            HorizontalDivider(color = Color(0xFF424242))
                            InfoRow(label = "NFC 卡號", value = "NFC-暫存") // API 暫無此資料
                        }
                        Spacer(modifier = Modifier.height(24.dp))

                        ProfileSection(title = "個人詳細資料") {
                            InfoRow(label = "電子郵件", value = userProfile.email, isClickable = true) {
                                Toast.makeText(context, "編輯電子郵件", Toast.LENGTH_SHORT).show()
                            }
                            HorizontalDivider(color = Color(0xFF424242))
                            InfoRow(label = "聯絡電話", value = userProfile.personnelprofile?.phone ?: "N/A", isClickable = true) {
                                Toast.makeText(context, "編輯聯絡電話", Toast.LENGTH_SHORT).show()
                            }
                            HorizontalDivider(color = Color(0xFF424242))
                            InfoRow(label = "駕照號碼", value = userProfile.personnelprofile?.licenseNumber ?: "N/A")
                            HorizontalDivider(color = Color(0xFF424242))
                            InfoRow(label = "駕照種類", value = userProfile.personnelprofile?.licenseType ?: "N/A")
                        }
                        Spacer(modifier = Modifier.height(24.dp))

                        // ⭐ 4. App 設定的資料來源改為 uiState.notificationSettings
                        ProfileSection(title = "App 設定") {
                            SettingsSwitchRow(
                                label = "接收危險事件通知",
                                isChecked = uiState.notificationSettings.receiveDangerousEvent,
                                onCheckedChange = { viewModel.onSettingChanged(event = it) }
                            )
                            SettingsSwitchRow(
                                label = "接收系統公告通知",
                                isChecked = uiState.notificationSettings.receiveSystemAnnouncements,
                                onCheckedChange = { viewModel.onSettingChanged(announcement = it) }
                            )
                        }
                        Spacer(modifier = Modifier.height(32.dp))

                        Button(
                            onClick = {
                                // 登出時清除 Token
                                TokenManager.clearToken()
                                navController.navigate("launch") {
                                    popUpTo(0)
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4A4A4A)),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("登出帳號", color = Color.White)
                        }
                        Spacer(modifier = Modifier.height(32.dp))
                    }
                }
            }
        }
    }
}