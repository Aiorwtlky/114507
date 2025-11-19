// 檔案路徑: app/src/main/java/com/example/mdgapp/MyHceService.kt

package com.example.mdgapp

import android.nfc.cardemulation.HostApduService
import android.os.Bundle
import android.util.Log

// 輔助函式：將十六進位字串轉為 Byte 陣列
private fun String.hexStringToByteArray(): ByteArray {
    val cleanHex = this.replace(":", "") // 移除冒號，確保格式正確
    check(cleanHex.length % 2 == 0) { "Hex string must have an even length" }
    return cleanHex.chunked(2)
        .map { it.toInt(16).toByte() }
        .toByteArray()
}

private fun ByteArray.toHexString(): String = joinToString("") { "%02X".format(it) }

// 建立 SELECT APDU 指令的輔助函式
private fun buildSelectApdu(aid: String): ByteArray {
    val header = "00A40400".hexStringToByteArray()
    val aidBytes = aid.hexStringToByteArray()
    val length = aidBytes.size.toByte()
    // APDU 格式: CLA INS P1 P2 Lc Data Le
    return header + byteArrayOf(length) + aidBytes
}

class MyHceService : HostApduService() {

    companion object {
        private const val TAG = "MyHceService"
        // 這個 AID 必須與 apduservice.xml 定義的一致 (F222222222)
        private const val SAMPLE_LOYALTY_CARD_AID = "F222222222"

        // ✅ 1. 定義您指定的固定 NFC 編號 (Hex 格式)
        private const val FIXED_NFC_ID = "EA:67:DA:12"

        // 預先計算好觸發指令
        private val SELECT_APDU = buildSelectApdu(SAMPLE_LOYALTY_CARD_AID)
    }

    override fun onDeactivated(reason: Int) {
        Log.d(TAG, "HCE 服務已停用，原因: $reason")
    }

    override fun processCommandApdu(commandApdu: ByteArray, extras: Bundle?): ByteArray {
        Log.i(TAG, "收到 APDU 命令: ${commandApdu.toHexString()}")

        // 檢查是否為車機發出的 Select AID 指令
        if (SELECT_APDU.contentEquals(commandApdu)) {
            Log.i(TAG, "AID 匹配成功！準備回傳固定 NFC 編號: $FIXED_NFC_ID")

            // ✅ 2. 將固定的 Hex 字串轉換為原始 Byte
            // 這裡不使用 UTF-8，而是直接解析 Hex，這是硬體通訊的標準做法
            val uidBytes = FIXED_NFC_ID.hexStringToByteArray()

            // 狀態碼 9000 代表成功
            val successStatus = "9000".hexStringToByteArray()

            // 回傳：[ID Bytes] + [Status Code]
            // 車機收到後會解析前面的 Byte 作為卡號
            return uidBytes + successStatus
        } else {
            Log.w(TAG, "收到的 APDU 與預期的不符，或是其他的指令")
            // 回傳「檔案未找到」或「不支援」
            return "6A82".hexStringToByteArray()
        }
    }
}