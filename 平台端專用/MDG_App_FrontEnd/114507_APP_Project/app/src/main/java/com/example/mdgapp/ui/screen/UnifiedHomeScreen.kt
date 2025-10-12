package com.example.mdgapp.ui.screen

import androidx.compose.foundation.BorderStroke
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
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.rememberVectorPainter
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.AsyncImage
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UnifiedHomeScreen(
    navController: NavController,
    profileViewModel: ProfileViewModel = viewModel()
) {
    val uiState by profileViewModel.uiState.collectAsState()
    val userProfile = uiState.userProfile

    // ✅ 修改重點：頁面載入時就取得使用者資料
    LaunchedEffect(Unit) {
        if (userProfile == null && !uiState.isLoading) {
            profileViewModel.fetchUserProfile()
        }
    }

    Scaffold(
        containerColor = iOsBackground,
        bottomBar = {
            BottomAppBar(
                containerColor = iOsComponentBackground.copy(alpha = 0.8f),
                contentColor = iOsTextPrimary,
                tonalElevation = 0.dp
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
                                tint = iOsBlue,
                                modifier = Modifier.size(32.dp)
                            )
                            Text("打卡", fontSize = 12.sp, color = iOsBlue)
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
                .padding(horizontal = 24.dp, vertical = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(40.dp))

            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(color = iOsBlue)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "正在載入個人資料...",
                        fontSize = 16.sp,
                        color = iOsTextSecondary
                    )
                }
                uiState.errorMessage != null -> {
                    Text(
                        text = "載入失敗: ${uiState.errorMessage}",
                        color = Color.Red,
                        fontSize = 14.sp
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
                userProfile != null -> {
                    val fullName = listOfNotNull(userProfile.lastName, userProfile.firstName).joinToString("")

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
                        text = (if (fullName.isBlank()) userProfile.username else fullName) ?: "讀取中...",
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = iOsTextPrimary
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "人員編號：${userProfile.personnelprofile?.personnelNumber ?: "N/A"}",
                        fontSize = 16.sp,
                        color = iOsTextSecondary
                    )
                }
            }

            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                RegisterButton(
                    icon = Icons.Default.Nfc,
                    text = "手機 NFC 註冊",
                    onClick = {
                        if (userProfile != null) {
                            navController.navigate("nfcCheckIn")
                        }
                    },
                    enabled = userProfile != null && !uiState.isLoading
                )
                Spacer(modifier = Modifier.height(16.dp))

                RegisterButton(
                    icon = Icons.Default.CreditCard,
                    text = "實體卡片註冊",
                    onClick = {
                        if (userProfile != null) {
                            navController.navigate("cardCheckIn")
                        }
                    },
                    enabled = userProfile != null && !uiState.isLoading
                )
            }

            TextButton(
                onClick = { navController.navigate("profile") },
                enabled = userProfile != null
            ) {
                Text("查看完整個人資料", color = iOsBlue, fontSize = 14.sp)
            }
        }
    }
}

@Composable
private fun RegisterButton(
    icon: ImageVector,
    text: String,
    onClick: () -> Unit,
    enabled: Boolean = true
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier
            .fillMaxWidth()
            .height(60.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = iOsComponentBackground,
            disabledContainerColor = iOsComponentBackground.copy(alpha = 0.5f)
        ),
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(3.dp, if (enabled) iOsBlue else iOsTextSecondary.copy(alpha = 0.3f))
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(
                imageVector = icon,
                contentDescription = text,
                tint = if (enabled) iOsTextSecondary else iOsTextSecondary.copy(alpha = 0.5f),
                modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Text(
                text = text,
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium,
                color = if (enabled) iOsTextPrimary else iOsTextPrimary.copy(alpha = 0.5f)
            )
        }
    }
}