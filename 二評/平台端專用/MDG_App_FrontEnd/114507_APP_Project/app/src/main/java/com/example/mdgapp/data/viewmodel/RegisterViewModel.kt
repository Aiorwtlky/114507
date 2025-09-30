// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/RegisterViewModel.kt

package com.example.mdgapp.data.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.model.PersonnelProfileRequest
import com.example.mdgapp.data.model.RegisterRequest
import com.example.mdgapp.data.remote.ApiService
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// 用來管理註冊畫面的所有狀態
data class RegisterUiState(
    // 輸入欄位的狀態
    val username: String = "",
    val password: String = "",
    val email: String = "",
    val firstName: String = "",
    val lastName: String = "",
    val personnelNumber: String = "",
    val gender: String = "MALE", // 預設值
    val licenseNumber: String = "",

    // 處理流程的狀態
    val isLoading: Boolean = false,
    val registrationError: String? = null,
    val isRegistrationSuccess: Boolean = false
)

class RegisterViewModel : ViewModel() {

    private val apiService: ApiService = RetrofitInstance.api
    private val _uiState = MutableStateFlow(RegisterUiState())
    val uiState = _uiState.asStateFlow()

    // 供 UI 呼叫，用來更新各個欄位的狀態
    fun onUsernameChange(value: String) = _uiState.update { it.copy(username = value) }
    fun onPasswordChange(value: String) = _uiState.update { it.copy(password = value) }
    fun onEmailChange(value: String) = _uiState.update { it.copy(email = value) }
    fun onFirstNameChange(value: String) = _uiState.update { it.copy(firstName = value) }
    fun onLastNameChange(value: String) = _uiState.update { it.copy(lastName = value) }
    fun onPersonnelNumberChange(value: String) = _uiState.update { it.copy(personnelNumber = value) }
    fun onGenderChange(value: String) = _uiState.update { it.copy(gender = value) }
    fun onLicenseNumberChange(value: String) = _uiState.update { it.copy(licenseNumber = value) }

    // UI 點擊「註冊」按鈕時呼叫此函式
    fun registerUser() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, registrationError = null) }

            // 1. 從目前的 state 組合出 API 需要的 request 物件
            val currentState = _uiState.value
            val request = RegisterRequest(
                username = currentState.username.trim(),
                password = currentState.password,
                email = currentState.email.trim(),
                firstName = currentState.firstName.trim(),
                lastName = currentState.lastName.trim(),
                personnelProfile = PersonnelProfileRequest(
                    personnelNumber = currentState.personnelNumber.trim(),
                    gender = currentState.gender,
                    licenseNumber = currentState.licenseNumber.trim()
                )
            )

            try {
                // 2. 呼叫 API
                val response = apiService.registerUser(request)

                // 3. 處理回應
                if (response.isSuccessful) {
                    Log.d("RegisterViewModel", "註冊成功: ${response.body()}")
                    _uiState.update { it.copy(isLoading = false, isRegistrationSuccess = true) }
                } else {
                    // 處理 API 回傳的錯誤，例如帳號已存在
                    val errorBody = response.errorBody()?.string()
                    Log.e("RegisterViewModel", "註冊失敗: ${response.code()}, $errorBody")
                    _uiState.update { it.copy(isLoading = false, registrationError = "註冊失敗: $errorBody") }
                }
            } catch (e: Exception) {
                // 處理網路連線等例外錯誤
                Log.e("RegisterViewModel", "註冊時發生例外", e)
                _uiState.update { it.copy(isLoading = false, registrationError = "網路錯誤，請稍後再試") }
            }
        }
    }
}