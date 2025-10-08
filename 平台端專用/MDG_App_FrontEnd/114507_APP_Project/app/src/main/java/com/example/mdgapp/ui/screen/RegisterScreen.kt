package com.example.mdgapp.ui.screen

import android.widget.Toast
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.RegisterViewModel

@Composable
fun RegisterScreen(navController: NavController, viewModel: RegisterViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    LaunchedEffect(uiState.isRegistrationSuccess) {
        if (uiState.isRegistrationSuccess) {
            Toast.makeText(context, "註冊成功！請登入", Toast.LENGTH_SHORT).show()
            navController.popBackStack()
        }
    }

    LaunchedEffect(uiState.registrationError) {
        uiState.registrationError?.let {
            Toast.makeText(context, it, Toast.LENGTH_LONG).show()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 32.dp),
        contentAlignment = Alignment.Center
    ) {
        // ✅ 3. 使用可捲動的 Column 並設定元件間距
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.verticalScroll(rememberScrollState())
        ) {
            Text("註冊新帳號", style = MaterialTheme.typography.headlineLarge)
            Spacer(modifier = Modifier.height(16.dp))

            // -- 帳號密碼 --
            OutlinedTextField(value = uiState.username, onValueChange = viewModel::onUsernameChange, label = { Text("設定帳號") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = uiState.email, onValueChange = viewModel::onEmailChange, label = { Text("Email") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email), modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = uiState.password, onValueChange = viewModel::onPasswordChange, label = { Text("設定密碼") }, visualTransformation = PasswordVisualTransformation(), modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = uiState.confirmPassword, onValueChange = viewModel::onConfirmPasswordChange, label = { Text("確認密碼") }, visualTransformation = PasswordVisualTransformation(), modifier = Modifier.fillMaxWidth())

            // -- 個人資料 --
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = uiState.lastName, onValueChange = viewModel::onLastNameChange, label = { Text("姓氏") }, modifier = Modifier.weight(1f))
                OutlinedTextField(value = uiState.firstName, onValueChange = viewModel::onFirstNameChange, label = { Text("名字") }, modifier = Modifier.weight(1f))
            }
            OutlinedTextField(value = uiState.personnelNumber, onValueChange = viewModel::onPersonnelNumberChange, label = { Text("員工編號") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = uiState.licenseNumber, onValueChange = viewModel::onLicenseNumberChange, label = { Text("駕照號碼") }, modifier = Modifier.fillMaxWidth())

            // -- 性別選擇 --
            Column(modifier = Modifier.fillMaxWidth()) {
                Text("性別", style = MaterialTheme.typography.bodyLarge)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    RadioButton(selected = uiState.gender == "MALE", onClick = { viewModel.onGenderChange("MALE") })
                    Text("男性", Modifier.clickable { viewModel.onGenderChange("MALE") })
                    Spacer(Modifier.width(16.dp))
                    RadioButton(selected = uiState.gender == "FEMALE", onClick = { viewModel.onGenderChange("FEMALE") })
                    Text("女性", Modifier.clickable { viewModel.onGenderChange("FEMALE") })
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // -- 按鈕 --
            Button(
                onClick = { viewModel.registerUser() },
                enabled = !uiState.isLoading,
                modifier = Modifier.fillMaxWidth().height(48.dp)
            ) {
                Text("註冊")
            }
            TextButton(onClick = { navController.popBackStack() }) {
                Text("已有帳號？返回登入")
            }

            if (uiState.isLoading) {
                CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
            }
        }
    }
}