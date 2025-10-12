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
import androidx.lifecycle.lifecycleScope
import androidx.navigation.NavHostController
import androidx.navigation.compose.rememberNavController
import com.example.mdgapp.data.viewmodel.BindingResultType
import com.example.mdgapp.data.viewmodel.NfcViewModel
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.navigation.AppNavGraph
import com.example.mdgapp.ui.theme.MyApplicationTheme
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach

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
        listenForLogoutEvents()
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

    private fun listenForLogoutEvents() {
        lifecycleScope.launchWhenStarted {
            MyApplication.logoutEvent
                .onEach {
                    val intent = Intent(this@MainActivity, MainActivity::class.java).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                    }
                    startActivity(intent)
                    finish()
                }
                .launchIn(this)
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

            val tag: Tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG) ?: return
            val currentRoute = navController.currentBackStackEntry?.destination?.route
            Log.d(TAG, "NFC 標籤偵測到，目前路由: $currentRoute")

            when (currentRoute) {
                "cardCheckIn" -> handleCardRegistration(tag)
                "NfcLogIn" -> handleNfcCheckIn(tag)
                else -> Log.d(TAG, "在非 NFC 功能頁面掃描到標籤，不執行操作。")
            }
        }
    }

    private fun handleCardRegistration(tag: Tag) {
        val uiState = profileViewModel.uiState.value
        val userProfile = uiState.userProfile

        if (uiState.isLoading) {
            runOnUiThread { Toast.makeText(this, "正在載入資料，請稍後再掃描", Toast.LENGTH_SHORT).show() }
            return
        }

        val currentUserId = userProfile?.personnelprofile?.personnelNumber
        if (currentUserId.isNullOrEmpty()) {
            Log.e(TAG, "無法取得使用者 Personnel Number")
            runOnUiThread { Toast.makeText(this, "錯誤：無法取得使用者員工編號", Toast.LENGTH_SHORT).show() }
            return
        }

        Log.d(TAG, "開始處理實體卡片註冊")
        Log.d(TAG, "使用者: ${userProfile?.username}, 準備寫入的ID: $currentUserId")

        val result = nfcHandler.handleCardRegistration(tag, currentUserId)
        handleRegistrationResult(result)
    }

    private fun handleRegistrationResult(result: NfcHandler.NfcResult) {
        runOnUiThread {
            when (result) {
                is NfcHandler.NfcResult.RegistrationSuccess -> {
                    Log.i(TAG, "========== 情境 1: 首次註冊 ==========")
                    Log.i(TAG, "卡片 UID: ${result.uid}")

                    // ✅ 呼叫後端綁定 API
                    nfcViewModel.bindNfcCard(result.uid, BindingResultType.FIRST_TIME_REGISTRATION)

                    // ✅ 顯示成功通知
                    Toast.makeText(
                        this,
                        "卡片註冊成功！\n卡號: ${result.uid}",
                        Toast.LENGTH_LONG
                    ).show()

                    // ✅ 返回上一頁
                    navController.popBackStack()
                }

                is NfcHandler.NfcResult.AlreadyRegisteredToCurrentUser -> {
                    Log.i(TAG, "========== 情境 2: 已註冊檢查 ==========")
                    Log.i(TAG, "卡片 UID: ${result.uid}")

                    // ✅✅✅ 關鍵修正：檢查後端綁定的卡號是否與當前卡片 UID 一致
                    val backendNfcCardId = profileViewModel.uiState.value.userProfile
                        ?.personnelprofile?.nfcCardId

                    Log.d(TAG, "後端綁定卡號: $backendNfcCardId")
                    Log.d(TAG, "當前卡片 UID: ${result.uid}")

                    if (backendNfcCardId == result.uid) {
                        // ✅ 情境 2: 卡片內 User ID 正確 + 後端綁定也正確
                        Log.i(TAG, "✅ 情境 2 確認: 該卡片已正確註冊")
                        Toast.makeText(
                            this,
                            "該卡片已註冊\n卡號: ${result.uid}",
                            Toast.LENGTH_SHORT
                        ).show()
                    } else {
                        // ⚠️ 情境 3: 卡片內寫了當前使用者的 ID，但後端綁定是其他卡片
                        // 這表示卡片被錯誤寫入，或者後端已綁定其他卡片
                        Log.w(TAG, "⚠️ 卡片內容正確但後端綁定不符")
                        Log.w(TAG, "這可能是測試卡或已被其他人使用的卡片")

                        Toast.makeText(
                            this,
                            "此卡片資料異常\n" +
                                    "您的註冊卡號: $backendNfcCardId\n" +
                                    "請使用正確的卡片",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }

                is NfcHandler.NfcResult.RegisteredToAnotherUser -> {
                    Log.w(TAG, "========== 情境 3: 已被他人註冊 ==========")
                    Log.w(TAG, "卡片 UID: ${result.uid}")
                    Log.w(TAG, "卡片持有者 ID: ${result.existingUserId}")

                    // ✅ 顯示警告通知
                    Toast.makeText(
                        this,
                        "此卡片已被其他人員註冊\n" +
                                "持有者編號: ${result.existingUserId}\n" +
                                "請詢問相關人員處理",
                        Toast.LENGTH_LONG
                    ).show()
                }

                is NfcHandler.NfcResult.Error -> {
                    Log.e(TAG, "========== 錯誤 ==========")
                    Log.e(TAG, "錯誤訊息: ${result.message}")

                    Toast.makeText(
                        this,
                        "❌ 操作失敗\n${result.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }

                else -> {
                    Log.w(TAG, "未預期的結果類型: $result")
                }
            }
        }
    }

    private fun handleNfcCheckIn(tag: Tag) {
        Log.d(TAG, "執行【NFC 打卡】操作...")
        val result = nfcHandler.readCardForCheckIn(tag)
        handleCheckInResult(result)
    }

    private fun handleCheckInResult(result: NfcHandler.NfcResult) {
        when (result) {
            is NfcHandler.NfcResult.ReadSuccess -> {
                Log.i(TAG, "--- NFC 打卡成功 ---")
                Log.i(TAG, "UID: ${result.uid}")
                runOnUiThread {
                    Toast.makeText(
                        this,
                        "✅ 打卡成功！\nUID: ${result.uid}",
                        Toast.LENGTH_SHORT
                    ).show()
                    navController.popBackStack()
                }
            }
            is NfcHandler.NfcResult.Error -> {
                Log.e(TAG, "--- NFC 打卡失敗 ---: ${result.message}")
                runOnUiThread {
                    Toast.makeText(
                        this,
                        "❌ 打卡失敗: ${result.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
            else -> {
                Log.w(TAG, "打卡時收到未預期的結果: $result")
            }
        }
    }
}