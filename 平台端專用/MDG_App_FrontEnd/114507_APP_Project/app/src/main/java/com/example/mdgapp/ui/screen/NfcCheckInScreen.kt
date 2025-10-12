package com.example.mdgapp.ui.screen

import android.provider.Settings
import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Nfc
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.NfcHandler
import com.example.mdgapp.data.viewmodel.BindingResultType
import com.example.mdgapp.data.viewmodel.NfcViewModel
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.ui.theme.iOsBackground
import com.example.mdgapp.ui.theme.iOsBlue
import com.example.mdgapp.ui.theme.iOsComponentBackground
import com.example.mdgapp.ui.theme.iOsTextPrimary
import com.example.mdgapp.ui.theme.iOsTextSecondary
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NfcCheckInScreen(
    navController: NavController,
    profileViewModel: ProfileViewModel = viewModel(),
    nfcViewModel: NfcViewModel = viewModel()
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

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

    // 處理註冊按鈕點擊
    fun handleRegisterClick() {
        if (userProfile == null) {
            Toast.makeText(context, "請先載入使用者資料", Toast.LENGTH_SHORT).show()
            return
        }

        scope.launch {
            try {
                // 獲取 Android ID 作為手機的唯一識別碼
                val androidId = Settings.Secure.getString(
                    context.contentResolver,
                    Settings.Secure.ANDROID_ID
                )

                // 生成手機 NFC UID (使用 Android ID 的後8位轉大寫)
                val phoneNfcUid = androidId
                    .takeLast(8)
                    .uppercase()
                    .padStart(8, '0')

                // 取得當前使用者已綁定的 UID (從 personnelprofile 的 nfcCardId)
                val currentUserUid = userProfile.personnelprofile?.nfcCardId

                // 判斷註冊邏輯
                when {
                    // 情境 1: 首次註冊
                    currentUserUid == null -> {
                        nfcViewModel.bindNfcCard(phoneNfcUid, BindingResultType.FIRST_TIME_REGISTRATION)
                        Toast.makeText(
                            context,
                            "✅ 手機 NFC 註冊成功！\nUID: $phoneNfcUid",
                            Toast.LENGTH_LONG
                        ).show()
                        navController.popBackStack()
                    }
                    // 情境 3: 已註冊相同 UID
                    currentUserUid == phoneNfcUid -> {
                        Toast.makeText(
                            context,
                            "ℹ️ 該手機 NFC 已綁定給您\nUID: $phoneNfcUid",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                    // 情境 2: 更新註冊
                    else -> {
                        nfcViewModel.bindNfcCard(phoneNfcUid, BindingResultType.UPDATE_REGISTRATION)
                        Toast.makeText(
                            context,
                            "🔄 已切換綁定至手機 NFC！\nUID: $phoneNfcUid",
                            Toast.LENGTH_LONG
                        ).show()
                        navController.popBackStack()
                    }
                }

            } catch (e: Exception) {
                Toast.makeText(
                    context,
                    "發生錯誤: ${e.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("手機 NFC 註冊") },
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
                            imageVector = Icons.Default.Nfc,
                            contentDescription = "手機 NFC 圖示",
                            tint = iOsBlue,
                            modifier = Modifier.size(120.dp)
                        )

                        Spacer(modifier = Modifier.height(32.dp))

                        Text(
                            "手機 NFC 註冊",
                            color = iOsTextPrimary,
                            fontSize = 28.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        Text(
                            "使用您的手機作為 NFC 裝置\n註冊後可用於打卡",
                            color = iOsTextSecondary,
                            fontSize = 16.sp,
                            textAlign = TextAlign.Center
                        )

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

                        // 註冊按鈕
                        Button(
                            onClick = { handleRegisterClick() },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(56.dp),
                            enabled = !nfcUiState.isBindingInProgress,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = iOsBlue
                            )
                        ) {
                            if (nfcUiState.isBindingInProgress) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(24.dp),
                                    color = Color.White,
                                    strokeWidth = 2.dp
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("註冊中...")
                            } else {
                                Text(
                                    "註冊手機 NFC",
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

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