package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

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
            delay(1000) // 模擬網路延遲

            val username = _uiState.value.username
            val password = _uiState.value.password

            // 模擬的登入驗證邏輯
            if (username == "driver" && password == "1234") {
                _uiState.update { it.copy(isLoading = false, isLoginSuccess = true) }
            } else {
                _uiState.update { it.copy(isLoading = false, loginError = "帳號或密碼錯誤") }
            }
        }
    }

    fun resetLoginState() {
        _uiState.update { it.copy(isLoginSuccess = false, loginError = null) }
    }
}