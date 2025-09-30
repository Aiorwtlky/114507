// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/RegisterScreen.kt

package com.example.mdgapp.ui.screen

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.RegisterViewModel
import com.example.mdgapp.ui.theme.MyApplicationTheme

@Composable
fun RegisterScreen(
    navController: NavController? = null,
    viewModel: RegisterViewModel = viewModel() // 獲取我們之前建立的 ViewModel
) {
    // 從 ViewModel 收集 UI 狀態
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    // 用於處理註冊成功或失敗後的單次事件 (例如跳轉頁面、顯示 Toast)
    LaunchedEffect(uiState.isRegistrationSuccess, uiState.registrationError) {
        if (uiState.isRegistrationSuccess) {
            Toast.makeText(context, "註冊成功！", Toast.LENGTH_SHORT).show()
            // 註冊成功後，導航到登入頁面
            navController?.navigate("login") {
                // 清除返回堆疊，讓使用者不能從登入頁按返回鍵回到註冊頁
                popUpTo("register") { inclusive = true }
            }
        }
        // 如果有錯誤訊息，就顯示出來
        uiState.registrationError?.let { error ->
            Toast.makeText(context, error, Toast.LENGTH_LONG).show()
        }
    }

    // 主畫面佈局
    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.background)
                .padding(horizontal = 32.dp)
                // 增加垂直滾動，防止鍵盤彈出時畫面超出
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text("建立帳號", fontSize = 48.sp, color = MaterialTheme.colorScheme.onBackground)
            Spacer(modifier = Modifier.height(24.dp))

            // --- 表單欄位 ---
            // 每個 TextField 的 value 和 onValueChange 都與 ViewModel 綁定
            OutlinedTextField(
                value = uiState.username,
                onValueChange = viewModel::onUsernameChange,
                label = { Text("帳號 (Username)") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = uiState.password,
                onValueChange = viewModel::onPasswordChange,
                label = { Text("密碼 (Password)") },
                visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = uiState.email,
                onValueChange = viewModel::onEmailChange,
                label = { Text("電子郵件 (Email)") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(16.dp))

            // 使用 Row 來並排姓氏和名字
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedTextField(
                    value = uiState.lastName,
                    onValueChange = viewModel::onLastNameChange,
                    label = { Text("姓氏") },
                    modifier = Modifier.weight(1f)
                )
                OutlinedTextField(
                    value = uiState.firstName,
                    onValueChange = viewModel::onFirstNameChange,
                    label = { Text("名字") },
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = uiState.personnelNumber,
                onValueChange = viewModel::onPersonnelNumberChange,
                label = { Text("員工編號") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = uiState.licenseNumber,
                onValueChange = viewModel::onLicenseNumberChange,
                label = { Text("駕照號碼") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(8.dp))

            // 性別選擇
            GenderSelector(
                selectedGender = uiState.gender,
                onGenderSelected = viewModel::onGenderChange
            )
            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = viewModel::registerUser, // 按鈕點擊時直接呼叫 ViewModel 的函式
                enabled = !uiState.isLoading, // 正在載入時，按鈕不可點擊
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text("確認註冊", fontSize = 20.sp)
            }
        }

        // 如果正在載入，顯示一個半透明的遮罩和進度條
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

// 為了讓 UI 更清晰，將性別選擇器獨立成一個 Composable
@Composable
private fun GenderSelector(selectedGender: String, onGenderSelected: (String) -> Unit) {
    val genderOptions = listOf("MALE", "FEMALE", "UNSPECIFIED")
    Column {
        Text("性別", color = MaterialTheme.colorScheme.onSurfaceVariant)
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            genderOptions.forEach { gender ->
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.weight(1f)
                ) {
                    RadioButton(
                        selected = (gender == selectedGender),
                        onClick = { onGenderSelected(gender) }
                    )
                    Text(
                        text = when(gender) {
                            "MALE" -> "男"
                            "FEMALE" -> "女"
                            else -> "未指定"
                        },
                        modifier = Modifier.padding(start = 4.dp),
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }
            }
        }
    }
}


@Preview(showBackground = true)
@Composable
fun PreviewRegisterScreen() {
    MyApplicationTheme {
        RegisterScreen()
    }
}