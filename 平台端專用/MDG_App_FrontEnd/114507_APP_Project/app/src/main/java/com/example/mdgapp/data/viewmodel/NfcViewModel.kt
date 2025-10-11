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
    val isBindingInProgress: Boolean = false,
    val successMessage: String? = null,
    val errorMessage: String? = null,
    val bindingResultType: BindingResultType? = null
)

enum class BindingResultType {
    FIRST_TIME_REGISTRATION,  // 首次註冊
    UPDATE_REGISTRATION,      // 更新註冊
    ALREADY_REGISTERED        // 已註冊
}

class NfcViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(NfcUiState())
    val uiState: StateFlow<NfcUiState> = _uiState.asStateFlow()

    /**
     * 綁定 NFC 卡片（後端 API 呼叫）
     */
    fun bindNfcCard(
        nfcSerialNumber: String,
        resultType: BindingResultType = BindingResultType.FIRST_TIME_REGISTRATION
    ) {
        viewModelScope.launch {
            _uiState.update {
                it.copy(
                    isBindingInProgress = true,
                    successMessage = null,
                    errorMessage = null,
                    bindingResultType = resultType
                )
            }

            val token = TokenManager.getToken()

            if (token.isNullOrBlank()) {
                _uiState.update {
                    it.copy(
                        isBindingInProgress = false,
                        errorMessage = "使用者未登入"
                    )
                }
                return@launch
            }

            try {
                val response = RetrofitInstance.api.bindNfcCard(
                    nfcBindRequest = NfcBindRequest(nfcId = nfcSerialNumber)
                )

                val successMsg = when (resultType) {
                    BindingResultType.FIRST_TIME_REGISTRATION ->
                        "卡片註冊成功！\n卡號: $nfcSerialNumber"
                    BindingResultType.UPDATE_REGISTRATION ->
                        "卡片資料更新成功！\n卡號: $nfcSerialNumber"
                    BindingResultType.ALREADY_REGISTERED ->
                        "該卡片已註冊\n卡號: $nfcSerialNumber"
                }

                _uiState.update {
                    it.copy(
                        isBindingInProgress = false,
                        successMessage = successMsg
                    )
                }

            } catch (e: HttpException) {
                val message = when (e.code()) {
                    409 -> "此 NFC 卡已被其他使用者綁定"
                    401 -> "身份驗證失敗，請重新登入"
                    403 -> "權限不足"
                    else -> "綁定失敗 (${e.code()})"
                }
                _uiState.update {
                    it.copy(
                        isBindingInProgress = false,
                        errorMessage = message
                    )
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(
                        isBindingInProgress = false,
                        errorMessage = "網路連線失敗"
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isBindingInProgress = false,
                        errorMessage = "發生未知的錯誤: ${e.message}"
                    )
                }
            }
        }
    }

    fun resetState() {
        _uiState.value = NfcUiState()
    }
}