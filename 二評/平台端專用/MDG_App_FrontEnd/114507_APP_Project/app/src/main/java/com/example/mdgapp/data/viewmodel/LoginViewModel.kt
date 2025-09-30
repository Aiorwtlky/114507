// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/LoginViewModel.kt

package com.example.mdgapp.data.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.local.TokenManager // 👈 【重點】1. 匯入我們建立的 TokenManager
import com.example.mdgapp.data.model.LoginRequest
import com.example.mdgapp.data.remote.ApiService
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// 管理登入畫面的所有狀態
data class LoginUiState(
    val username: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val loginError: String? = null,
    val isLoginSuccess: Boolean = false
)

class LoginViewModel : ViewModel() {

    private val apiService: ApiService = RetrofitInstance.api
    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState = _uiState.asStateFlow()

    // 供 UI 呼叫，更新帳號和密碼的狀態
    fun onUsernameChange(value: String) = _uiState.update { it.copy(username = value) }
    fun onPasswordChange(value: String) = _uiState.update { it.copy(password = value) }

    fun loginUser() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, loginError = null) }

            val request = LoginRequest(
                username = _uiState.value.username.trim(),
                password = _uiState.value.password
            )

            try {
                val response = apiService.login(request)

                if (response.isSuccessful && response.body() != null) {
                    val token = response.body()!!.token
                    Log.d("LoginViewModel", "登入成功, Token: $token")

                    // ▼▼▼▼▼ 【重點】2. 替換掉 TODO，實際呼叫 TokenManager 來儲存 Token ▼▼▼▼▼
                    TokenManager.saveToken(token)

                    _uiState.update { it.copy(isLoading = false, isLoginSuccess = true) }
                } else {
                    val errorBody = response.errorBody()?.string()
                    Log.e("LoginViewModel", "登入失敗: ${response.code()}, $errorBody")
                    _uiState.update { it.copy(isLoading = false, loginError = "帳號或密碼錯誤") }
                }
            } catch (e: Exception) {
                Log.e("LoginViewModel", "登入時發生例外", e)
                _uiState.update { it.copy(isLoading = false, loginError = "網路錯誤，請稍後再試") }
            }
        }
    }
}