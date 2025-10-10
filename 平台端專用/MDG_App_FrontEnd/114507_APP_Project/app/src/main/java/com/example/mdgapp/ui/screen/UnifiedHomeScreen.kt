package com.example.mdgapp.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.CreditCard
import androidx.compose.material.icons.filled.Nfc
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ProfileViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UnifiedHomeScreen(
    navController: NavController,
    viewModel: ProfileViewModel = viewModel()
) {
    // ⭐ 1. 訂閱整個 UiState
    val uiState by viewModel.uiState.collectAsState()
    val userProfile = uiState.userProfile

    Scaffold(
        containerColor = Color.Black,
        bottomBar = {
            BottomAppBar(
                containerColor = Color(0xFF1A1A1A),
                contentColor = Color.White
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center
                ) {
                    IconButton(
                        onClick = { navController.navigate("NfcLogIn") },
                        modifier = Modifier.size(64.dp)
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Default.CheckCircle,
                                contentDescription = "打卡",
                                tint = Color.White,
                                modifier = Modifier.size(32.dp)
                            )
                            Text("打卡", fontSize = 12.sp, color = Color.White)
                        }
                    }
                }
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(40.dp))

            // ⭐ 2. 根據 UiState 顯示個人資料或載入動畫
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator()
                }
                uiState.errorMessage != null -> {
                    Text(text = uiState.errorMessage ?: "發生錯誤", color = Color.White)
                }
                userProfile != null -> {
                    Box(
                        modifier = Modifier
                            .size(100.dp)
                            .clip(CircleShape)
                            .background(Color(0xFF2A2A2A)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Person,
                            contentDescription = "個人頭像",
                            tint = Color.White,
                            modifier = Modifier.size(60.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(16.dp))

                    // ⭐ 3. 更新資料來源
                    Text(
                        text = "${userProfile.lastName}${userProfile.firstName}",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "員工編號：${userProfile.personnelprofile?.personnelNumber ?: "N/A"}",
                        fontSize = 16.sp,
                        color = Color.Gray
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    Text(text = "車輛：MDG-0000", fontSize = 16.sp, color = Color.Gray) // API 暫無
                    Spacer(modifier = Modifier.height(8.dp))

                    Text(text = "群組：總部第一車隊", fontSize = 16.sp, color = Color.Gray) // API 暫無
                    Spacer(modifier = Modifier.height(8.dp))

                    Text(text = "NFC 卡號：NFC-暫存", fontSize = 16.sp, color = Color.Gray) // API 暫無
                }
            }

            Spacer(modifier = Modifier.height(60.dp))

            RegisterButton(
                icon = Icons.Default.Nfc,
                text = "手機 NFC 註冊",
                onClick = { navController.navigate("nfcCheckIn") }
            )
            Spacer(modifier = Modifier.height(20.dp))

            RegisterButton(
                icon = Icons.Default.CreditCard,
                text = "實體卡片註冊",
                onClick = { navController.navigate("cardCheckIn") }
            )
            Spacer(modifier = Modifier.weight(1f))

            TextButton(onClick = { navController.navigate("profile") }) {
                Text("查看完整個人資料", color = Color.Gray, fontSize = 14.sp)
            }
        }
    }
}

@Composable
private fun RegisterButton(
    icon: ImageVector,
    text: String,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(70.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = Color(0xFF2A2A2A)
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(
                imageVector = icon,
                contentDescription = text,
                tint = Color.White,
                modifier = Modifier.size(32.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Text(
                text = text,
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium,
                color = Color.White
            )
        }
    }
}