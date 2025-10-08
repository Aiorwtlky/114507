package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// ✅ 1. 將所有需要的欄位加回 UiState
data class RegisterUiState(
    val username: String = "",
    val password: String = "",
    val confirmPassword: String = "",
    val email: String = "",
    val lastName: String = "",
    val firstName: String = "",
    val personnelNumber: String = "",
    val gender: String = "MALE", // 預設值 MALE 或 FEMALE
    val licenseNumber: String = "",
    val isLoading: Boolean = false,
    val registrationError: String? = null,
    val isRegistrationSuccess: Boolean = false
)

class RegisterViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(RegisterUiState())
    val uiState = _uiState.asStateFlow()

    // ✅ 2. 加入所有欄位對應的更新函式
    fun onUsernameChange(value: String) = _uiState.update { it.copy(username = value) }
    fun onPasswordChange(value: String) = _uiState.update { it.copy(password = value) }
    fun onConfirmPasswordChange(value: String) = _uiState.update { it.copy(confirmPassword = value) }
    fun onEmailChange(value: String) = _uiState.update { it.copy(email = value) }
    fun onLastNameChange(value: String) = _uiState.update { it.copy(lastName = value) }
    fun onFirstNameChange(value: String) = _uiState.update { it.copy(firstName = value) }
    fun onPersonnelNumberChange(value: String) = _uiState.update { it.copy(personnelNumber = value) }
    fun onGenderChange(value: String) = _uiState.update { it.copy(gender = value) }
    fun onLicenseNumberChange(value: String) = _uiState.update { it.copy(licenseNumber = value) }

    fun registerUser() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, registrationError = null) }
            delay(1500) // 模擬網路延遲

            val state = _uiState.value
            if (state.password != state.confirmPassword) {
                _uiState.update { it.copy(isLoading = false, registrationError = "兩次輸入的密碼不一致") }
                return@launch
            }
            if (state.username.isBlank() || state.password.isBlank() || state.email.isBlank() || state.lastName.isBlank() || state.firstName.isBlank()) {
                _uiState.update { it.copy(isLoading = false, registrationError = "必填欄位不得為空") }
                return@launch
            }

            // 模擬註冊成功
            _uiState.update { it.copy(isLoading = false, isRegistrationSuccess = true) }
        }
    }
}