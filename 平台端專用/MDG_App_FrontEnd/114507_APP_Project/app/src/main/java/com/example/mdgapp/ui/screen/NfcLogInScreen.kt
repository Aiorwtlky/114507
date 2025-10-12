package com.example.mdgapp.ui.screen

import android.util.Log
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Nfc
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.mdgapp.ui.theme.iOsBackground
import com.example.mdgapp.ui.theme.iOsBlue
import com.example.mdgapp.ui.theme.iOsComponentBackground
import com.example.mdgapp.ui.theme.iOsTextPrimary
import com.example.mdgapp.ui.theme.iOsTextSecondary

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NfcLogInScreen(navController: NavController) {
    LaunchedEffect(Unit) {
        Log.d("NfcApp", "進入「打卡」畫面，等待掃描讀取...")
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("NFC 打卡") },
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
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.padding(horizontal = 32.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Nfc,
                    contentDescription = "NFC 圖示",
                    tint = iOsBlue,
                    modifier = Modifier.size(120.dp)
                )

                Spacer(modifier = Modifier.height(32.dp))

                Text(
                    "NFC 打卡",
                    color = iOsTextPrimary,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    "請將您的手機或已註冊的卡片\n靠近感應點",
                    color = iOsTextSecondary,
                    fontSize = 16.sp,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}