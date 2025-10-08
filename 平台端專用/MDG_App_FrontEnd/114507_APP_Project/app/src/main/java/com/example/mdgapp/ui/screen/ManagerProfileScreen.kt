package com.example.mdgapp.ui.screen
/*
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
import com.example.mdgapp.data.viewmodel.ManagerProfileViewModel
import com.example.mdgapp.ui.component.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerProfileScreen(
    navController: NavController,
    viewModel: ManagerProfileViewModel = viewModel()
) {
    val userProfile by viewModel.userProfile.collectAsState()
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("帳號管理") },
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

                // 管理權限資訊
                ProfileSection(title = "管理權限") {
                    InfoRow(label = "管理群組", value = profile.groupName)
                }
                Spacer(modifier = Modifier.height(24.dp))

                // ✅ 複製自 ProfileScreen：個人詳細資料區塊
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

                // ✅ 複製自 ProfileScreen：已連結的帳號區塊
                ProfileSection(title = "已連結的帳號") {
                    profile.linkedAccounts.forEach { account ->
                        LinkedAccountRow(account = account)
                        HorizontalDivider(color = Color(0xFF424242))
                    }
                    TextButton(
                        onClick = { Toast.makeText(context, "新增帳號", Toast.LENGTH_SHORT).show() },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("新增其他平台帳號")
                    }
                }
                Spacer(modifier = Modifier.height(24.dp))

                // ✅ 複製自 ProfileScreen：App 設定區塊 (微調文字)
                ProfileSection(title = "App 設定") {
                    SettingsSwitchRow(
                        label = "接收團隊危險事件通知",
                        isChecked = profile.notificationSettings.receiveDangerousEvent,
                        onCheckedChange = { viewModel.onSettingChanged(event = it) }
                    )
                    SettingsSwitchRow(
                        label = "接收系統公告通知",
                        isChecked = profile.notificationSettings.receiveSystemAnnouncements,
                        onCheckedChange = { viewModel.onSettingChanged(announcement = it) }
                    )
                    SettingsSwitchRow(
                        label = "僅在 Wi-Fi 環境下載",
                        isChecked = profile.notificationSettings.downloadOnlyOnWifi,
                        onCheckedChange = { viewModel.onSettingChanged(wifiOnly = it) }
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
}*/