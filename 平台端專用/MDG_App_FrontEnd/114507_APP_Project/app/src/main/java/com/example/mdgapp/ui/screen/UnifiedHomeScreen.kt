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
import androidx.compose.ui.graphics.vector.rememberVectorPainter // ⭐ 新增 import
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
    viewModel: ProfileViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val userProfile = uiState.userProfile

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
                }
                uiState.errorMessage != null -> {
                    Text(text = uiState.errorMessage ?: "發生錯誤", color = Color.Red)
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
                        // ⭐ 修正重點：使用 rememberVectorPainter 將 ImageVector 轉為 Painter
                        error = rememberVectorPainter(image = Icons.Default.Person),
                        placeholder = rememberVectorPainter(image = Icons.Default.Person)
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = if(fullName.isBlank()) userProfile.username else fullName,
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = iOsTextPrimary
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "員工編號：${userProfile.personnelprofile?.personnelNumber ?: "N/A"}",
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
                    onClick = { navController.navigate("nfcCheckIn") }
                )
                Spacer(modifier = Modifier.height(16.dp))

                RegisterButton(
                    icon = Icons.Default.CreditCard,
                    text = "實體卡片註冊",
                    onClick = { navController.navigate("cardCheckIn") }
                )
            }

            TextButton(onClick = { navController.navigate("profile") }) {
                Text("查看完整個人資料", color = iOsBlue, fontSize = 14.sp)
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
            .height(60.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = iOsComponentBackground
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(
                imageVector = icon,
                contentDescription = text,
                tint = iOsTextSecondary,
                modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Text(
                text = text,
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium,
                color = iOsTextPrimary
            )
        }
    }
}