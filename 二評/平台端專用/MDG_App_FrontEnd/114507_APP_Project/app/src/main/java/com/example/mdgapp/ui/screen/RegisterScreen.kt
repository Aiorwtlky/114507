package com.example.mdgapp.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.NavController
import com.example.mdgapp.ui.theme.MyApplicationTheme // 確保您的 theme 路徑正確

@Composable
fun RegisterScreen(navController: NavController? = null) {
    var driverId by remember { mutableStateOf("") }
    var driverName by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var deviceId by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("註冊", fontSize = 48.sp, color = MaterialTheme.colorScheme.onBackground)
        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = driverId,
            onValueChange = { driverId = it },
            label = { Text("駕駛編號") },
        )
        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = driverName,
            onValueChange = { driverName = it },
            label = { Text("駕駛姓名") }
        )
        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("密碼") },
            visualTransformation = PasswordVisualTransformation()
        )
        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = deviceId,
            onValueChange = { deviceId = it },
            label = { Text("綁定裝置序號") }
        )
        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = {
                // --- ✅ 這裡是修改後的核心邏輯 ---
                if (driverId.isNotBlank()) {
                    when (driverId.first().uppercaseChar()) {
                        'M' -> {
                            // 駕駛編號第一個字母為 M，導航到管理者主頁
                            navController?.navigate("managerHome") {
                                popUpTo("register") { inclusive = true }
                            }
                        }
                        'D' -> {
                            // 駕駛編號第一個字母為 D，導航到駕駛者主頁
                            navController?.navigate("home") {
                                popUpTo("register") { inclusive = true }
                            }
                        }
                        else -> {
                            // 可以加上錯誤提示，例如一個 Toast
                            println("無效的駕駛編號開頭")
                        }
                    }
                }
            },
            shape = CircleShape
        ) {
            Text("確認註冊", fontSize = 20.sp)
        }
    }
}

@Preview(
    showSystemUi = true,
    showBackground = true,
    backgroundColor = 0xFF0A1F44,
    name = "Register Preview - 深藍白字"
)
@Composable
fun PreviewRegisterScreen() {
    MyApplicationTheme(darkTheme = true) {
        RegisterScreen()
    }
}