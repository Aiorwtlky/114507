// 檔案路徑: app/src/main/java/com/example/mdgapp/data/viewmodel/NfcViewModel.kt

package com.example.mdgapp.data.viewmodel

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
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

class NfcViewModel(application: Application) : AndroidViewModel(application) {

    private val _uiState = MutableStateFlow(NfcUiState())
    val uiState: StateFlow<NfcUiState> = _uiState.asStateFlow()

    /**
     * 綁定 NFC 裝置（後端 API 呼叫）
     */
    fun bindNfcCard(
        nfcSerialNumber: String,
        resultType: BindingResultType = BindingResultType.FIRST_TIME_REGISTRATION,
        isPhoneNfc: Boolean = false // 新增參數以區分是手機還是卡片
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
                // 呼叫後端 API
                val response = RetrofitInstance.api.bindNfcCard(
                    nfcBindRequest = NfcBindRequest(nfcId = nfcSerialNumber)
                )

                // ✅ 如果是手機 NFC 且後端綁定成功，就將 UID 儲存到 SharedPreferences
                if (isPhoneNfc) {
                    savePhoneUidToPrefs(nfcSerialNumber)
                }

                val deviceName = if (isPhoneNfc) "手機 NFC" else "卡片"
                val successMsg = when (resultType) {
                    BindingResultType.FIRST_TIME_REGISTRATION ->
                        "$deviceName 註冊成功！\nUID: $nfcSerialNumber"
                    BindingResultType.UPDATE_REGISTRATION ->
                        "綁定已更新至此 $deviceName！\nUID: $nfcSerialNumber"
                    BindingResultType.ALREADY_REGISTERED ->
                        "該 $deviceName 已註冊\nUID: $nfcSerialNumber"
                }

                _uiState.update {
                    it.copy(
                        isBindingInProgress = false,
                        successMessage = successMsg
                    )
                }

            } catch (e: HttpException) {
                val message = when (e.code()) {
                    409 -> "此 NFC 裝置已被其他使用者綁定"
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

    /**
     * 新增一個私有函式，用於將手機的 UID 儲存到 SharedPreferences
     */
    private fun savePhoneUidToPrefs(uid: String) {
        val context = getApplication<Application>().applicationContext
        val sharedPrefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
        with(sharedPrefs.edit()) {
            putString("phone_nfc_uid", uid)
            apply()
        }
    }

    fun resetState() {
        _uiState.value = NfcUiState()
    }
}