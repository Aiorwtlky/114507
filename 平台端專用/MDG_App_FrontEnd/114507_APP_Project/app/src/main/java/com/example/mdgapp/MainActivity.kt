package com.example.mdgapp

import android.app.PendingIntent
import android.content.Intent
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.example.mdgapp.data.model.UserProfile
import com.example.mdgapp.data.model.UserProfileResponse
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.navigation.AppNavGraph
import com.example.mdgapp.ui.theme.MyApplicationTheme
import com.example.mdgapp.data.model.NotificationSettings

class MainActivity : ComponentActivity() {

    private var nfcAdapter: NfcAdapter? = null
    private lateinit var pendingIntent: PendingIntent

    private val nfcHandler by lazy { NfcHandler(this) }
    private lateinit var navController: NavHostController
    private val TAG = "NfcApp"

    private val profileViewModel: ProfileViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        initNfc()

        setContent {
            MyApplicationTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    navController = rememberNavController()
                    AppNavGraph(navController = navController)
                }
            }
        }
    }

    private fun initNfc() {
        nfcAdapter = NfcAdapter.getDefaultAdapter(this)
        if (nfcAdapter == null) {
            Toast.makeText(this, "此裝置不支援 NFC", Toast.LENGTH_LONG).show()
        }

        val intent = Intent(this, javaClass).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
        pendingIntent = PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_MUTABLE)
    }

    override fun onResume() {
        super.onResume()
        nfcAdapter?.enableForegroundDispatch(this, pendingIntent, null, null)
    }

    override fun onPause() {
        super.onPause()
        nfcAdapter?.disableForegroundDispatch(this)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        val action = intent.action
        if (action == NfcAdapter.ACTION_NDEF_DISCOVERED ||
            action == NfcAdapter.ACTION_TECH_DISCOVERED ||
            action == NfcAdapter.ACTION_TAG_DISCOVERED) {

            Log.d(TAG, "成功捕獲 NFC Intent, Action: $action")
            val tag: Tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG) ?: return

            val currentRoute = navController.currentBackStackEntry?.destination?.route
            Log.d(TAG, "NFC 標籤偵測到，目前路由: $currentRoute")

            when (currentRoute) {
                "cardCheckIn" -> {
                    // ⭐ 修正 1: 從 uiState 中取得 userProfile
                    val userProfileFromApi = profileViewModel.uiState.value.userProfile

                    if (userProfileFromApi == null) {
                        Log.e(TAG, "無法獲取使用者資料，ViewModel 中的 Profile 為 null")
                        runOnUiThread { Toast.makeText(this, "錯誤：無法獲取使用者資料", Toast.LENGTH_SHORT).show() }
                        return
                    }

                    // ⭐ 修正 2: 將 API 的 UserProfileResponse 轉換為本地的 UserProfile
                    val localUserProfile = userProfileFromApi.toLocalUserProfile()

                    Log.d(TAG, "準備從 ViewModel 寫入個人資料: $localUserProfile")

                    val result = nfcHandler.writeUserProfile(tag, localUserProfile)
                    handleNfcResult(result)
                    if (result is NfcHandler.NfcResult.WriteSuccess) {
                        runOnUiThread { navController.popBackStack() }
                    }
                }

                "NfcLogIn" -> {
                    Log.d(TAG, "執行【打卡】讀取操作...")
                    val result = nfcHandler.readUserProfile(intent)
                    handleNfcResult(result)
                    if (result is NfcHandler.NfcResult.ReadSuccess) {
                        runOnUiThread { navController.popBackStack() }
                    }
                }

                else -> {
                    Log.d(TAG, "在非 NFC 功能頁面掃描到標籤，不執行操作。")
                }
            }
        }
    }

    private fun handleNfcResult(result: NfcHandler.NfcResult) {
        when (result) {
            is NfcHandler.NfcResult.WriteSuccess -> {
                Log.i(TAG, "--- NFC 註冊成功 ---")
                Log.i(TAG, "寫入資料 (JSON): ${result.writtenData}")
                Log.i(TAG, "讀回驗證: ${result.readBackData}")
                runOnUiThread { Toast.makeText(this, "註冊成功！", Toast.LENGTH_SHORT).show() }
            }
            is NfcHandler.NfcResult.ReadSuccess -> {
                Log.i(TAG, "--- NFC 讀取成功 ---")
                Log.i(TAG, "讀取到的 UserProfile 物件: ${result.userProfile}")
                runOnUiThread { Toast.makeText(this, "讀取成功！", Toast.LENGTH_SHORT).show() }
            }
            is NfcHandler.NfcResult.Error -> {
                Log.e(TAG, "--- NFC 操作失敗 ---: ${result.message}")
                runOnUiThread { Toast.makeText(this, "操作失敗: ${result.message}", Toast.LENGTH_LONG).show() }
            }
        }
    }

    /**
     * 輔助轉換函式：將從 API 獲取的 UserProfileResponse 轉換為 NFC 寫入所需的 UserProfile。
     */
    private fun UserProfileResponse.toLocalUserProfile(): UserProfile {
        // 這個函式負責將從網路 API 取得的資料格式 (UserProfileResponse)
        // 轉換為您 NFC 處理邏輯需要的本地資料格式 (UserProfile)
        return UserProfile(
            fullName = "${this.lastName}${this.firstName}",
            employeeId = this.personnelprofile?.personnelNumber ?: "N/A",
            avatarUrl = this.personnelprofile?.avatar ?: "",
            email = this.email,
            phone = this.personnelprofile?.phone ?: "N/A",
            // 注意：以下欄位在 UserProfileResponse 中不存在，暫時給予預設值
            currentVehiclePlate = "MDG-0000",
            groupName = "總部第一車隊",
            nfcCardNumber = "NFC-暫存", // 寫入時這個欄位可能不需要，取決於您的 NfcHandler 實作
            licenseNumber = this.personnelprofile?.licenseNumber ?: "N/A",
            licenseClass = this.personnelprofile?.licenseType ?: "N/A",
            linkedAccounts = emptyList(), // 暫時給予空列表

            // ⭐ 修正：提供一個預設的 NotificationSettings 物件，而不是 null
            notificationSettings = NotificationSettings(
                receiveDangerousEvent = true,
                receiveSystemAnnouncements = true,
                downloadOnlyOnWifi = true
            )
        )
    }
}