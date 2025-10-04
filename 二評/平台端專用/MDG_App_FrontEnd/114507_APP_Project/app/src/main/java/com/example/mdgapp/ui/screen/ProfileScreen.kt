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
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.ui.component.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    navController: NavController,
    viewModel: ProfileViewModel = viewModel()
) {
    val userProfile by viewModel.userProfile.collectAsState()
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
        userProfile?.let { profile ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(horizontal = 16.dp)
                    .verticalScroll(rememberScrollState())
            ) {
                ProfileHeader(name = profile.fullName, employeeId = profile.employeeId)

                // 車輛與群組資訊
                ProfileSection(title = "車輛與群組") {
                    InfoRow(label = "目前駕駛車輛", value = profile.currentVehiclePlate)
                    HorizontalDivider(color = Color(0xFF424242))
                    InfoRow(label = "所屬群組", value = profile.groupName)
                }
                Spacer(modifier = Modifier.height(24.dp))

                // =======================================================
                // ✅ 新增的「數據分析」區塊，按鈕會出現在這裡
                // =======================================================
                ProfileSection(title = "數據分析") {
                    InfoRow(label = "個人歷史數據總覽", value = "", isClickable = true) {
                        navController.navigate("driverHistory")
                    }
                }
                Spacer(modifier = Modifier.height(24.dp))
                // =======================================================

                // 個人詳細資料
                ProfileSection(title = "個人詳細資料") {
                    InfoRow(label = "電子郵件", value = profile.email, isClickable = true) {
                        Toast.makeText(context, "編輯電子郵件", Toast.LENGTH_SHORT).show()
                    }
                    HorizontalDivider(color = Color(0xFF424242))
                    InfoRow(label = "聯絡電話", value = profile.phone, isClickable = true) {
                        Toast.makeText(context, "編輯聯絡電話", Toast.LENGTH_SHORT).show()
                    }
                    HorizontalDivider(color = Color(0xFF424242))
                    InfoRow(label = "駕照號碼", value = profile.licenseNumber)
                    HorizontalDivider(color = Color(0xFF424242))
                    InfoRow(label = "駕照種類", value = profile.licenseClass)
                }
                Spacer(modifier = Modifier.height(24.dp))

                // App 設定
                ProfileSection(title = "App 設定") {
                    SettingsSwitchRow(
                        label = "接收危險事件通知",
                        isChecked = profile.notificationSettings.receiveDangerousEvent,
                        onCheckedChange = { viewModel.onSettingChanged(event = it) }
                    )
                    SettingsSwitchRow(
                        label = "接收系統公告通知",
                        isChecked = profile.notificationSettings.receiveSystemAnnouncements,
                        onCheckedChange = { viewModel.onSettingChanged(announcement = it) }
                    )
                }
                Spacer(modifier = Modifier.height(32.dp))

                // 登出按鈕
                Button(
                    onClick = {
                        navController.navigate("launch") {
                            popUpTo(0) // 清除整個返回堆疊
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4A4A4A)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("登出帳號", color = Color.White)
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        } ?: Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
    }
}