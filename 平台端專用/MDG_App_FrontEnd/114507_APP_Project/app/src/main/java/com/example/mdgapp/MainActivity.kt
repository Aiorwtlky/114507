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

        // 開始監聽全域的登出事件
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

    /**
     * 監聽來自 MyApplication 的 logoutEvent
     */
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

    /**
     * 處理 NFC 標籤掃描事件的核心邏輯
     */
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
                // 處理「實體卡片註冊」的流程
                "cardCheckIn" -> {
                    handleCardRegistration(tag)
                }

                // 處理「NFC登入/打卡」的流程
                "NfcLogIn" -> {
                    handleNfcLogin(tag)
                }

                else -> {
                    Log.d(TAG, "在非 NFC 功能頁面掃描到標籤，不執行操作。")
                }
            }
        }
    }

    /**
     * 處理實體卡片註冊邏輯
     */
    private fun handleCardRegistration(tag: Tag) {
        val uiState = profileViewModel.uiState.value

        // 如果正在載入，等待載入完成
        if (uiState.isLoading) {
            Log.d(TAG, "個人資料載入中，等待資料...")
            runOnUiThread {
                Toast.makeText(this, "正在載入資料，請稍後再掃描", Toast.LENGTH_SHORT).show()
            }
            return
        }

        // 如果載入失敗，提示使用者
        if (uiState.errorMessage != null) {
            Log.e(TAG, "個人資料載入失敗: ${uiState.errorMessage}")
            runOnUiThread {
                Toast.makeText(this, "資料載入失敗，請返回重試", Toast.LENGTH_SHORT).show()
            }
            return
        }

        // 檢查使用者資料
        val userProfile = uiState.userProfile
        val currentDriverId = userProfile?.personnelprofile?.personnelNumber

        if (currentDriverId.isNullOrBlank()) {
            Log.e(TAG, "無法獲取人員編號，userProfile 為 null")
            runOnUiThread {
                Toast.makeText(this, "錯誤：無法取得人員編號", Toast.LENGTH_SHORT).show()
            }
            return
        }

        Log.d(TAG, "開始處理卡片註冊，當前人員編號: $currentDriverId")
        val result = nfcHandler.handleCardRegistration(tag, currentDriverId)
        handleCardRegistrationResult(result)
    }

    /**
     * 處理 NFC 登入/打卡邏輯
     */
    private fun handleNfcLogin(tag: Tag) {
        Log.d(TAG, "執行【讀取卡片實體編號】操作...")
        val result = nfcHandler.readCardSerialNumber(tag)
        handleNfcLoginResult(result)
    }

    /**
     * 統一處理卡片註冊的結果
     */
    private fun handleCardRegistrationResult(result: NfcHandler.NfcResult) {
        when (result) {
            // 情境 1: 首次註冊成功
            is NfcHandler.NfcResult.WriteSuccess -> {
                if (result.isNewCard) {
                    Log.i(TAG, "--- 卡片首次註冊成功 ---")
                    Log.i(TAG, "人員編號: ${result.driverId}")
                    Log.i(TAG, "卡片實體編號: ${result.serialNumber}")

                    // 呼叫後端 API 綁定卡片
                    nfcViewModel.bindNfcCard(
                        result.serialNumber,
                        com.example.mdgapp.data.viewmodel.BindingResultType.FIRST_TIME_REGISTRATION
                    )

                    runOnUiThread {
                        Toast.makeText(
                            this,
                            "卡片寫入成功！正在綁定至後端...",
                            Toast.LENGTH_SHORT
                        ).show()
                        navController.popBackStack()
                    }
                }
            }

            // 情境 2: 卡片資料更新成功
            is NfcHandler.NfcResult.UpdateSuccess -> {
                Log.i(TAG, "--- 卡片資料更新成功 ---")
                Log.i(TAG, "舊人員編號: ${result.oldDriverId}")
                Log.i(TAG, "新人員編號: ${result.newDriverId}")
                Log.i(TAG, "卡片實體編號: ${result.serialNumber}")

                // 呼叫後端 API 更新卡片綁定
                nfcViewModel.bindNfcCard(
                    result.serialNumber,
                    com.example.mdgapp.data.viewmodel.BindingResultType.UPDATE_REGISTRATION
                )

                runOnUiThread {
                    Toast.makeText(
                        this,
                        "卡片更新成功！正在同步至後端...",
                        Toast.LENGTH_SHORT
                    ).show()
                    navController.popBackStack()
                }
            }

            // 情境 3: 卡片已註冊
            is NfcHandler.NfcResult.AlreadyRegistered -> {
                Log.i(TAG, "--- 卡片已註冊 ---")
                Log.i(TAG, "人員編號: ${result.driverId}")
                Log.i(TAG, "卡片實體編號: ${result.serialNumber}")

                runOnUiThread {
                    Toast.makeText(
                        this,
                        "該卡片已註冊給您\n人員編號: ${result.driverId}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }

            // 錯誤處理
            is NfcHandler.NfcResult.Error -> {
                Log.e(TAG, "--- 卡片註冊失敗 ---: ${result.message}")
                runOnUiThread {
                    Toast.makeText(
                        this,
                        "操作失敗: ${result.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }

            else -> {
                Log.w(TAG, "未預期的結果類型: $result")
            }
        }
    }

    /**
     * 統一處理 NFC 登入/打卡的結果
     */
    private fun handleNfcLoginResult(result: NfcHandler.NfcResult) {
        when (result) {
            is NfcHandler.NfcResult.ReadSuccess -> {
                Log.i(TAG, "--- NFC 卡片實體編號讀取成功 ---")
                Log.i(TAG, "讀取到的卡片實體編號: ${result.serialNumber}")

                // TODO: 在這裡呼叫 ViewModel 的方法，將這個 serialNumber 用於登入或打卡
                // 例如： loginViewModel.loginWithNfc(result.serialNumber)

                runOnUiThread {
                    Toast.makeText(
                        this,
                        "打卡成功！\n卡號: ${result.serialNumber}",
                        Toast.LENGTH_SHORT
                    ).show()
                    navController.popBackStack()
                }
            }

            is NfcHandler.NfcResult.Error -> {
                Log.e(TAG, "--- NFC 讀取失敗 ---: ${result.message}")
                runOnUiThread {
                    Toast.makeText(
                        this,
                        "讀取失敗: ${result.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }

            else -> {
                Log.w(TAG, "未預期的結果類型: $result")
            }
        }
    }
}