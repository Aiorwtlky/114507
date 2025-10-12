package com.example.mdgapp

import android.nfc.Tag
import android.nfc.tech.MifareClassic
import android.util.Log
import java.io.IOException
import java.nio.charset.Charset

class NfcHandler(private val activity: MainActivity) {

    private val TAG = "NfcHandler"

    companion object {
        private val KNOWN_KEYS = listOf(
            MifareClassic.KEY_DEFAULT,
            MifareClassic.KEY_NFC_FORUM,
            MifareClassic.KEY_MIFARE_APPLICATION_DIRECTORY,
            byteArrayOf(0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
            byteArrayOf(0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte())
        )
        const val SECTOR_INDEX = 1
        const val BLOCK_INDEX = 4
    }

    sealed class NfcResult {
        data class RegistrationSuccess(val uid: String) : NfcResult()
        data class AlreadyRegisteredToCurrentUser(val uid: String) : NfcResult()
        data class RegisteredToAnotherUser(val uid: String, val existingUserId: String) : NfcResult()
        data class ReadSuccess(val uid: String, val deviceType: DeviceType) : NfcResult()
        data class Error(val message: String) : NfcResult()
    }

    enum class DeviceType {
        PHYSICAL_CARD,
        PHONE_NFC
    }

    fun handleCardRegistration(tag: Tag, currentUserId: String): NfcResult {
        val cardUid = tag.id.toHexString()
        Log.d(TAG, "========== 卡片註冊流程 (統一連線管理) ==========")
        Log.d(TAG, "卡片 UID: $cardUid")
        Log.d(TAG, "目前登入使用者 ID: $currentUserId")

        val mifare = MifareClassic.get(tag)
        if (mifare == null) {
            Log.e(TAG, "❌ 此卡不支援 MIFARE Classic。")
            return NfcResult.Error("卡片類型不支援")
        }

        try {
            mifare.connect()

            if (!authenticate(mifare, SECTOR_INDEX)) {
                return NfcResult.Error("金鑰驗證失敗，無法存取卡片")
            }

            val userIdFromCard = readFromConnectedCard(mifare)
            Log.d(TAG, "從卡片解析出的乾淨 ID: '${userIdFromCard ?: "空"}'")

            return when {
                userIdFromCard.isNullOrEmpty() -> {
                    Log.i(TAG, "✅ 情境 1: 卡片為空，準備寫入...")
                    if (writeToConnectedCard(mifare, currentUserId)) {
                        Log.i(TAG, "✅ 寫入成功！")
                        NfcResult.RegistrationSuccess(cardUid)
                    } else {
                        Log.e(TAG, "❌ 寫入失敗。")
                        NfcResult.Error("寫入資料到卡片失敗")
                    }
                }
                userIdFromCard == currentUserId -> {
                    Log.i(TAG, "ℹ️ 情境 2: 該卡片已正確註冊給您。")
                    NfcResult.AlreadyRegisteredToCurrentUser(cardUid)
                }
                else -> {
                    Log.w(TAG, "⚠️ 情境 3: 此卡片已被其他人員註冊。")
                    NfcResult.RegisteredToAnotherUser(cardUid, userIdFromCard)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ 處理卡片註冊時發生嚴重錯誤: ${e.message}", e)
            return NfcResult.Error("操作卡片時發生錯誤")
        } finally {
            if (mifare.isConnected) {
                try {
                    mifare.close()
                } catch (e: IOException) {
                    Log.e(TAG, "關閉連線時發生錯誤", e)
                }
            }
        }
    }

    private fun authenticate(mifare: MifareClassic, sectorIndex: Int): Boolean {
        for (key in KNOWN_KEYS) {
            try {
                if (mifare.authenticateSectorWithKeyA(sectorIndex, key)) {
                    Log.i(TAG, "✅ 磁區 $sectorIndex 驗證成功 (Key A: ${key.toHexString()})")
                    return true
                }
            } catch (e: IOException) {
                // 忽略並繼續
            }
        }
        Log.e(TAG, "❌ 磁區 $sectorIndex 驗證失敗，所有已知金鑰均無效。")
        return false
    }

    private fun readFromConnectedCard(mifare: MifareClassic): String? {
        val blockData = mifare.readBlock(BLOCK_INDEX)
        Log.d(TAG, "[讀取] Block $BLOCK_INDEX 原始 hex: ${blockData.toHexString()}")

        val cleanString = String(blockData, Charset.defaultCharset())
            .replace(Regex("\\p{Cntrl}"), "")
            .trim()

        return if (cleanString.isNotEmpty()) cleanString else null
    }

    private fun writeToConnectedCard(mifare: MifareClassic, userId: String): Boolean {
        return try {
            val userIdBytes = userId.toByteArray(Charset.defaultCharset())
            if (userIdBytes.size > 16) {
                Log.e(TAG, "❌ User ID 過長 (${userIdBytes.size} bytes)，無法寫入。")
                return false
            }

            val blockData = ByteArray(16) { 0 }
            System.arraycopy(userIdBytes, 0, blockData, 0, userIdBytes.size)

            Log.d(TAG, "[準備寫入] ${blockData.toHexString()}")
            mifare.writeBlock(BLOCK_INDEX, blockData)
            true
        } catch (e: IOException) {
            Log.e(TAG, "❌ 寫入 Block $BLOCK_INDEX 時發生 I/O 錯誤", e)
            false
        }
    }

    // ✅✅✅ 關鍵修正：恢復這個函式的完整實作 ✅✅✅
    fun readCardForCheckIn(tag: Tag): NfcResult {
        return try {
            val cardUid = tag.id.toHexString()
            NfcResult.ReadSuccess(uid = cardUid, deviceType = DeviceType.PHYSICAL_CARD)
        } catch (e: Exception) {
            NfcResult.Error("讀取失敗: ${e.message}")
        }
    }

    private fun ByteArray.toHexString(): String =
        joinToString(":") { "%02X".format(it) }
}