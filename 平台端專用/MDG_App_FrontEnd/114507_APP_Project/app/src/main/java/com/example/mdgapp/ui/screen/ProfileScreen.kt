// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/ProfileScreen.kt

package com.example.mdgapp.ui.screen

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.rememberVectorPainter
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.AsyncImage
import com.example.mdgapp.data.local.TokenManager
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    navController: NavController,
    viewModel: ProfileViewModel = viewModel()
) {
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
                    containerColor = iOsBackground,
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
                .padding(paddingValues)
        ) {
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center),
                        color = iOsBlue
                    )
                }
                uiState.errorMessage != null -> {
                    Text(
                        text = uiState.errorMessage ?: "發生錯誤",
                        color = Color.Red,
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                userProfile != null -> {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState())
                            .padding(16.dp)
                    ) {
                        val fullName = listOfNotNull(userProfile.lastName, userProfile.firstName).joinToString("")

                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            AsyncImage(
                                model = userProfile.personnelprofile?.avatar,
                                contentDescription = "個人頭像",
                                modifier = Modifier
                                    .size(100.dp)
                                    .clip(CircleShape)
                                    .background(iOsComponentBackground),
                                contentScale = ContentScale.Crop,
                                error = rememberVectorPainter(image = Icons.Default.Person),
                                placeholder = rememberVectorPainter(image = Icons.Default.Person)
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = if(fullName.isBlank()) userProfile.username else fullName,
                                color = iOsTextPrimary,
                                fontSize = 24.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = userProfile.personnelprofile?.personnelNumber ?: "N/A",
                                color = iOsTextSecondary,
                                fontSize = 16.sp
                            )
                        }
                        Spacer(modifier = Modifier.height(32.dp))

                        ProfileSection {
                            InfoRow(label = "目前駕駛車輛", value = "MDG-0000")
                            ListDivider()
                            InfoRow(label = "所屬群組", value = "總部第一車隊")
                            ListDivider()
                            InfoRow(label = "NFC 卡號", value = userProfile.personnelprofile?.nfcCardId ?: "未綁定")
                        }
                        Spacer(modifier = Modifier.height(24.dp))

                        ProfileSection {
                            InfoRow(label = "電子郵件", value = userProfile.email)
                            ListDivider()
                            InfoRow(label = "聯絡電話", value = userProfile.personnelprofile?.phone ?: "N/A")
                            ListDivider()
                            InfoRow(label = "駕照號碼", value = userProfile.personnelprofile?.licenseNumber ?: "N/A")
                            ListDivider()
                            InfoRow(label = "駕照種類", value = userProfile.personnelprofile?.licenseType ?: "N/A")
                        }
                        Spacer(modifier = Modifier.height(24.dp))

                        ProfileSection {
                            SettingsSwitchRow(
                                label = "接收危險事件通知",
                                isChecked = uiState.notificationSettings.receiveDangerousEvent,
                                onCheckedChange = { viewModel.onSettingChanged(event = it) }
                            )
                            ListDivider()
                            SettingsSwitchRow(
                                label = "接收系統公告通知",
                                isChecked = uiState.notificationSettings.receiveSystemAnnouncements,
                                onCheckedChange = { viewModel.onSettingChanged(announcement = it) }
                            )
                        }
                        Spacer(modifier = Modifier.height(32.dp))

                        Button(
                            onClick = {
                                TokenManager.clearToken()
                                navController.navigate("launch") { popUpTo(0) }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = iOsComponentBackground),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(50.dp),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text("登出帳號", color = Color.Red, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ProfileSection(content: @Composable ColumnScope.() -> Unit) {
    val shape = RoundedCornerShape(12.dp)
    Column(
        modifier = Modifier
            .fillMaxWidth()
            // ✅ 修改點：將邊框應用到 Modifier 上
            .border(BorderStroke(2.dp, iOsBlue), shape = shape)
            .clip(shape)
            .background(iOsComponentBackground)
    ) {
        content()
    }
}

@Composable
fun InfoRow(label: String, value: String, isClickable: Boolean = false, onClick: () -> Unit = {}) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = isClickable, onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = label, color = iOsTextPrimary, fontSize = 16.sp)
        Text(text = value, color = iOsTextSecondary, fontSize = 16.sp)
    }
}

@Composable
fun SettingsSwitchRow(label: String, isChecked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = label, color = iOsTextPrimary, fontSize = 16.sp)
        Switch(
            checked = isChecked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = Color.White,
                checkedTrackColor = iOsBlue, // <-- 也把 Switch 的顏色改為藍色以求一致
                uncheckedThumbColor = Color.White,
                uncheckedTrackColor = Color.Gray.copy(alpha = 0.5f),
                uncheckedBorderColor = Color.Transparent
            )
        )
    }
}

@Composable
fun ListDivider() {
    HorizontalDivider(
        modifier = Modifier.padding(start = 16.dp),
        thickness = 0.5.dp,
        color = iOsSeparator
    )
}