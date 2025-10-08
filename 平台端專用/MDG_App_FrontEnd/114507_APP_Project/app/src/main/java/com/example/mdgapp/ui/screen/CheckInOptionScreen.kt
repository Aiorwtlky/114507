package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CreditCard
import androidx.compose.material.icons.filled.Nfc
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CheckInOptionScreen(navController: NavController) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("選擇打卡方式") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回")
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 32.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            OptionButton(
                text = "手機 NFC 登入",
                icon = { Icon(Icons.Default.Nfc, contentDescription = null, modifier = Modifier.size(ButtonDefaults.IconSize)) },
                onClick = { navController.navigate("nfcCheckIn") }
            )
            Spacer(modifier = Modifier.height(24.dp))
            OptionButton(
                text = "感應卡登入",
                icon = { Icon(Icons.Default.CreditCard, contentDescription = null, modifier = Modifier.size(ButtonDefaults.IconSize)) },
                onClick = { navController.navigate("cardCheckIn") }
            )
        }
    }
}

@Composable
private fun OptionButton(
    text: String,
    icon: @Composable () -> Unit,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(60.dp),
        shape = MaterialTheme.shapes.medium,
        colors = ButtonDefaults.buttonColors(
            containerColor = Color(0xFF2A2A2E),
            contentColor = Color.White
        )
    ) {
        icon()
        Spacer(Modifier.size(ButtonDefaults.IconSpacing))
        Text(text, fontSize = 18.sp)
    }
}