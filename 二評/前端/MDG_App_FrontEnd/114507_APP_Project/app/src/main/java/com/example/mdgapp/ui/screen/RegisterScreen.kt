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
import com.example.mdgapp.ui.theme.MyApplicationTheme
import androidx.navigation.NavController

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
            label = { Text("駕駛編號") }
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
                navController?.navigate("home")
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
