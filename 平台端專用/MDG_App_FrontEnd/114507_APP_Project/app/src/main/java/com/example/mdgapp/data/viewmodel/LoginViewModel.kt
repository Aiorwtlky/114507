package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.local.TokenManager
import com.example.mdgapp.data.model.LoginRequest
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

data class LoginUiState(
    val username: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val loginError: String? = null,
    val isLoginSuccess: Boolean = false
)

class LoginViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    fun onUsernameChange(value: String) = _uiState.update { it.copy(username = value) }
    fun onPasswordChange(value: String) = _uiState.update { it.copy(password = value) }

    fun loginUser() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, loginError = null) }

            try {
                val response = RetrofitInstance.api.loginUser(
                    LoginRequest(
                        username = _uiState.value.username,
                        password = _uiState.value.password
                    )
                )

                // ⭐ 登入成功後，立刻將 access token 存起來！
                TokenManager.saveToken(response.access)

                _uiState.update { it.copy(isLoading = false, isLoginSuccess = true) }

            } catch (e: HttpException) {
                // HTTP 錯誤 (例如: 401 Unauthorized)
                _uiState.update { it.copy(isLoading = false, loginError = "帳號或密碼錯誤") }
            } catch (e: IOException) {
                // 網路連線錯誤
                _uiState.update { it.copy(isLoading = false, loginError = "網路連線失敗，請稍後再試") }
            } catch (e: Exception) {
                // 其他未預期的錯誤
                _uiState.update { it.copy(isLoading = false, loginError = "發生未知的錯誤") }
            }
        }
    }

    fun resetLoginState() {
        _uiState.update { it.copy(isLoginSuccess = false, loginError = null) }
    }
}