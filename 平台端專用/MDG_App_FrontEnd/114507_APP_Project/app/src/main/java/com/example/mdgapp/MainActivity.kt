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
import com.example.mdgapp.data.model.NotificationSettings
import com.example.mdgapp.data.model.UserProfile
import com.example.mdgapp.data.model.UserProfileResponse
import com.example.mdgapp.data.viewmodel.NfcViewModel
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.navigation.AppNavGraph
import com.example.mdgapp.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {

    private var nfcAdapter: NfcAdapter? = null
    private lateinit var pendingIntent: PendingIntent

    private val nfcHandler by lazy { NfcHandler(this) }
    private lateinit var navController: NavHostController
    private val TAG = "NfcApp"

    private val profileViewModel: ProfileViewModel by viewModels()
    private val nfcViewModel: NfcViewModel by viewModels()

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
                    val userProfileFromApi = profileViewModel.uiState.value.userProfile
                    if (userProfileFromApi == null) {
                        Log.e(TAG, "無法獲取使用者資料，ViewModel 中的 Profile 為 null")
                        runOnUiThread { Toast.makeText(this, "錯誤：個人資料尚未載入完成，請稍候再試", Toast.LENGTH_SHORT).show() }
                        return
                    }

                    val scannedSerialNumber = tag.id.toHexString()
                    Log.d(TAG, "掃描到的卡片序號: $scannedSerialNumber")

                    val existingNfcId = userProfileFromApi.personnelprofile?.nfcCardId
                    Log.d(TAG, "使用者已綁定的卡片序號: $existingNfcId")

                    val localUserProfile = userProfileFromApi.toLocalUserProfile(scannedSerialNumber)

                    if (!existingNfcId.isNullOrBlank() && existingNfcId.equals(scannedSerialNumber, ignoreCase = true)) {
                        Log.i(TAG, "偵測到為同一張已綁定卡片，執行資料更新流程...")

                        val result = nfcHandler.writeUserProfile(tag, localUserProfile)
                        if (result is NfcHandler.NfcResult.WriteSuccess) {
                            Log.i(TAG, "卡片上的個人資料已更新成功。")
                            runOnUiThread { Toast.makeText(this, "卡片資料已更新", Toast.LENGTH_SHORT).show() }
                        } else if (result is NfcHandler.NfcResult.Error) {
                            Log.e(TAG, "更新卡片資料時發生錯誤: ${result.message}")
                            runOnUiThread { Toast.makeText(this, "更新失敗: ${result.message}", Toast.LENGTH_LONG).show() }
                        }
                        navController.popBackStack()

                    } else {
                        val message = if (existingNfcId.isNullOrBlank()) "首次綁定新卡" else "更換為新的卡片"
                        Log.i(TAG, "$message，執行完整註冊流程...")

                        Log.d(TAG, "準備寫入個人資料: $localUserProfile")
                        val result = nfcHandler.writeUserProfile(tag, localUserProfile)
                        handleNfcResult(result)
                    }
                }
                "NfcLogIn" -> {
                    Log.d(TAG, "執行【打卡】讀取操作...")
                    val result = nfcHandler.readUserProfile(intent)
                    handleNfcResult(result)
                }
                else -> {
                    Log.d(TAG, "在非 NFC 功能頁面掃描到標籤，不執行操作。")
                }
            }
        }
    }

    // ⭐ 修正重點：補上 when 判斷式中缺少的 is ReadSuccess 和 is Error 兩種情況
    private fun handleNfcResult(result: NfcHandler.NfcResult) {
        when (result) {
            is NfcHandler.NfcResult.WriteSuccess -> {
                Log.i(TAG, "--- NFC 卡片寫入成功 (首次/更換) ---")
                Log.i(TAG, "卡片序號: ${result.serialNumber}")

                Log.d(TAG, "卡片寫入成功，準備將序號 ${result.serialNumber} 回傳伺服器進行綁定...")
                nfcViewModel.bindNfcCard(result.serialNumber)

                Log.d(TAG, "命令 ProfileViewModel 重新整理以同步最新資料...")
                profileViewModel.fetchUserProfile()

                runOnUiThread {
                    Toast.makeText(this, "卡片註冊成功！正在同步資料...", Toast.LENGTH_LONG).show()
                    navController.popBackStack()
                }
            }
            is NfcHandler.NfcResult.ReadSuccess -> {
                Log.i(TAG, "--- NFC 讀取成功 ---")
                Log.i(TAG, "讀取到的 UserProfile 物件: ${result.userProfile}")
                runOnUiThread {
                    Toast.makeText(this, "打卡成功！", Toast.LENGTH_SHORT).show()
                    navController.popBackStack()
                }
            }
            is NfcHandler.NfcResult.Error -> {
                Log.e(TAG, "--- NFC 操作失敗 ---: ${result.message}")
                runOnUiThread { Toast.makeText(this, "操作失敗: ${result.message}", Toast.LENGTH_LONG).show() }
            }
        }
    }

    private fun ByteArray.toHexString(): String = joinToString("") { "%02X".format(it) }

    private fun UserProfileResponse.toLocalUserProfile(serialNumber: String): UserProfile {
        val fullName = listOfNotNull(this.lastName, this.firstName).joinToString("")

        return UserProfile(
            fullName = if(fullName.isBlank()) this.username else fullName,
            employeeId = this.personnelprofile?.personnelNumber ?: "N/A",
            avatarUrl = this.personnelprofile?.avatar ?: "",
            email = this.email,
            phone = this.personnelprofile?.phone ?: "N/A",
            currentVehiclePlate = "MDG-0000",
            groupName = "總部第一車隊",
            nfcCardNumber = serialNumber,
            licenseNumber = this.personnelprofile?.licenseNumber ?: "N/A",
            licenseClass = this.personnelprofile?.licenseType ?: "N/A",
            linkedAccounts = emptyList(),
            notificationSettings = NotificationSettings(
                receiveDangerousEvent = true,
                receiveSystemAnnouncements = true,
                downloadOnlyOnWifi = true
            )
        )
    }
}