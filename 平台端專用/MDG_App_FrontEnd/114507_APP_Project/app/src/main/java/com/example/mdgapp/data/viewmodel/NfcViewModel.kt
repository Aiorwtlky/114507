package com.example.mdgapp.data.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.mdgapp.data.local.TokenManager
import com.example.mdgapp.data.model.NfcBindRequest
import com.example.mdgapp.data.remote.RetrofitInstance
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

data class NfcUiState(
    val isLoading: Boolean = false,
    val successMessage: String? = null,
    val errorMessage: String? = null
)

class NfcViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(NfcUiState())
    val uiState: StateFlow<NfcUiState> = _uiState.asStateFlow()

    fun bindNfcCard(nfcSerialNumber: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, successMessage = null, errorMessage = null) }

            val token = TokenManager.getToken()

            if (token.isNullOrBlank()) {
                _uiState.update { it.copy(isLoading = false, errorMessage = "使用者未登入") }
                return@launch
            }

            try {
                // ⭐ 修正：直接呼叫 api.bindNfcCard，因為 token 已由 AuthInterceptor 自動處理
                val response = RetrofitInstance.api.bindNfcCard(
                    nfcBindRequest = NfcBindRequest(nfcId = nfcSerialNumber)
                )
                _uiState.update { it.copy(isLoading = false, successMessage = response.success) }

            } catch (e: HttpException) {
                val message = if (e.code() == 409) "此 NFC 卡已被其他使用者綁定" else "綁定失敗"
                _uiState.update { it.copy(isLoading = false, errorMessage = message) }
            } catch (e: IOException) {
                _uiState.update { it.copy(isLoading = false, errorMessage = "網路連線失敗") }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, errorMessage = "發生未知的錯誤") }
            }
        }
    }

    fun resetState() {
        _uiState.value = NfcUiState()
    }
}