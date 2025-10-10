package com.example.mdgapp

import android.content.Context
import android.nfc.cardemulation.HostApduService
import android.os.Bundle
import android.util.Log
import com.example.mdgapp.data.viewmodel.ProfileViewModel
import com.example.mdgapp.AppConstants.HCE_PREFS_NAME
import com.example.mdgapp.AppConstants.PROFILE_JSON_KEY

class MyHostApduService : HostApduService() {

    private val TAG = "HceService"

    // ⭐ 修改處：將輔助函式移動到 companion object 內部
    companion object {
        val SW_OK = hexStringToByteArray("9000")
        val SW_DATA_NOT_FOUND = hexStringToByteArray("6A82")
        val SW_INS_NOT_SUPPORTED = hexStringToByteArray("6D00")
        val SELECT_APDU_HEADER = hexStringToByteArray("00A40400")

        // 輔助函式：將 Byte 陣列轉為十六進制字串 (方便 Log 顯示)
        fun byteArrayToHexString(bytes: ByteArray): String {
            return bytes.joinToString("") { "%02x".format(it).uppercase() }
        }

        // 輔助函式：將十六進制字串轉為 Byte 陣列
        fun hexStringToByteArray(hex: String): ByteArray {
            check(hex.length % 2 == 0) { "Hex string must have an even length" }
            return hex.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
        }
    }

    override fun onDeactivated(reason: Int) {
        Log.d(TAG, "HCE 服務已停用，原因: $reason")
    }

    override fun processCommandApdu(commandApdu: ByteArray, extras: Bundle?): ByteArray {
        Log.i(TAG, "收到 APDU 指令: ${byteArrayToHexString(commandApdu)}")

        if (isSelectAidApdu(commandApdu)) {
            Log.d(TAG, "指令為 SELECT AID，回應成功 (SW_OK)。")
            return SW_OK
        }

        Log.d(TAG, "指令為讀取資料，正在從 SharedPreferences 獲取 Profile...")
        val sharedPrefs = getSharedPreferences(HCE_PREFS_NAME, Context.MODE_PRIVATE)
        val profileJson = sharedPrefs.getString(PROFILE_JSON_KEY, null)

        return if (!profileJson.isNullOrEmpty()) {
            val dataBytes = profileJson.toByteArray(Charsets.UTF_8)
            Log.d(TAG, "成功讀取 Profile JSON，長度: ${dataBytes.size} bytes。準備回傳資料...")
            dataBytes + SW_OK
        } else {
            Log.w(TAG, "在 SharedPreferences 中找不到 Profile JSON 資料。")
            SW_DATA_NOT_FOUND
        }
    }

    private fun isSelectAidApdu(apdu: ByteArray): Boolean {
        return apdu.size >= SELECT_APDU_HEADER.size &&
                apdu.copyOfRange(0, SELECT_APDU_HEADER.size).contentEquals(SELECT_APDU_HEADER)
    }
}