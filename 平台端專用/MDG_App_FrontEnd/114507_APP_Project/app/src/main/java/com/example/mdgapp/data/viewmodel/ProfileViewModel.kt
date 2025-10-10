package com.example.mdgapp.data.viewmodel

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.local.TokenManager
import com.example.mdgapp.data.model.NotificationSettings
import com.example.mdgapp.data.model.UserProfileResponse
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

data class ProfileUiState(
    val isLoading: Boolean = true,
    val userProfile: UserProfileResponse? = null,
    val errorMessage: String? = null,
    val notificationSettings: NotificationSettings = NotificationSettings(
        receiveDangerousEvent = true,
        receiveSystemAnnouncements = true,
        downloadOnlyOnWifi = false
    )
)

class ProfileViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    init {
        fetchUserProfile()
    }

    fun fetchUserProfile() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }

            val token = TokenManager.getToken()

            if (token.isNullOrBlank()) {
                _uiState.update { it.copy(isLoading = false, errorMessage = "使用者未登入") }
                return@launch
            }

            try {
                // ⭐ 修正重點 1：直接呼叫 getUserProfile()，不需手動傳入 token
                val response = RetrofitInstance.api.getUserProfile()
                _uiState.update { it.copy(isLoading = false, userProfile = response) }

            } catch (e: HttpException) {
                val errorMsg = if (e.code() == 401) "登入已過期，請重新登入" else "無法載入資料"
                _uiState.update { it.copy(isLoading = false, errorMessage = errorMsg) }
            } catch (e: IOException) {
                _uiState.update { it.copy(isLoading = false, errorMessage = "網路連線失敗") }
            } catch (e: Exception) {
                // ⭐ 修正重點 2：加入詳細的錯誤日誌，方便我們除錯
                Log.e("ViewModelError", "解析 UserProfile 時發生未知錯誤", e)
                _uiState.update { it.copy(isLoading = false, errorMessage = "發生未知的錯誤") }
            }
        }
    }

    fun onSettingChanged(
        event: Boolean? = null,
        announcement: Boolean? = null,
        wifiOnly: Boolean? = null
    ) {
        _uiState.update { currentState ->
            currentState.copy(
                notificationSettings = currentState.notificationSettings.copy(
                    receiveDangerousEvent = event ?: currentState.notificationSettings.receiveDangerousEvent,
                    receiveSystemAnnouncements = announcement ?: currentState.notificationSettings.receiveSystemAnnouncements,
                    downloadOnlyOnWifi = wifiOnly ?: currentState.notificationSettings.downloadOnlyOnWifi
                )
            )
        }
    }
}