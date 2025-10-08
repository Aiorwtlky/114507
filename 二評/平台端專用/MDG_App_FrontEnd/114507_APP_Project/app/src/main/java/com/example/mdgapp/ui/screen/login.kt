// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/login.kt

package com.example.mdgapp.ui.screen

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.LoginViewModel

@Composable
fun LoginScreen(
    navController: NavController,
    viewModel: LoginViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    LaunchedEffect(uiState.isLoginSuccess, uiState.loginError) {
        if (uiState.isLoginSuccess) {
            Toast.makeText(context, "登入成功！", Toast.LENGTH_SHORT).show()
            // ✅ 登入成功後，跳轉到主頁面，並清除所有舊頁面
            navController.navigate("home") {
                popUpTo(0)
            }
        }
        uiState.loginError?.let { error ->
            Toast.makeText(context, error, Toast.LENGTH_LONG).show()
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background)
                .padding(32.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("吾駕仙", fontSize = 48.sp, color = MaterialTheme.colorScheme.onBackground)
            Text("駕駛員登入", fontSize = 24.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(modifier = Modifier.height(32.dp))

            OutlinedTextField(
                value = uiState.username,
                onValueChange = viewModel::onUsernameChange,
                label = { Text("帳號") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = uiState.password,
                onValueChange = viewModel::onPasswordChange,
                label = { Text("密碼") },
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(32.dp))

            Button(
                onClick = viewModel::loginUser,
                enabled = !uiState.isLoading,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text("登入", fontSize = 20.sp)
            }

            // ✅ 移除註冊連結
            // Spacer(modifier = Modifier.height(16.dp))
            // ClickableText(
            //     text = AnnotatedString("還沒有帳號？點此註冊"),
            //     onClick = { navController.navigate("register") },
            //     style = TextStyle(
            //         color = MaterialTheme.colorScheme.primary,
            //         textDecoration = TextDecoration.Underline
            //     )
            // )
        }

        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(MaterialTheme.colorScheme.background.copy(alpha = 0.5f)),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
    }
}