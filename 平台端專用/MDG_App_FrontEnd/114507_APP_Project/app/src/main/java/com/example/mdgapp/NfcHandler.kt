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
        const val BLOCK_INDEX = 5  // ✅ 改用 Block 5 試試看
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
        Log.d(TAG, "========== 卡片註冊流程 ==========")
        Log.d(TAG, "卡片 UID: $cardUid")
        Log.d(TAG, "目前登入使用者 ID: $currentUserId")

        val userIdFromCard = readUserIdFromCard(tag)
        Log.d(TAG, "從卡片讀取到的 User ID: '${userIdFromCard ?: "(空白)"}'")
        Log.d(TAG, "比對結果: 卡片='$userIdFromCard' vs 當前='$currentUserId', 相同=${userIdFromCard == currentUserId}")

        return when {
            // 情境 1: 卡片為空 (第一次註冊)
            userIdFromCard.isNullOrEmpty() -> {
                Log.i(TAG, "✅ 情境 1: 卡片為空，執行首次註冊")
                val writeSuccess = writeUserIdToCard(tag, currentUserId)
                if (writeSuccess) {
                    Log.i(TAG, "✅ 寫入成功: $currentUserId")
                    NfcResult.RegistrationSuccess(cardUid)
                } else {
                    Log.e(TAG, "❌ 寫入失敗")
                    NfcResult.Error("無法寫入資料到卡片")
                }
            }

            // 情境 2: 卡片中的 ID 與當前使用者 ID 完全相同
            userIdFromCard == currentUserId -> {
                Log.i(TAG, "✅ 情境 2: 卡片已註冊給當前使用者")
                NfcResult.AlreadyRegisteredToCurrentUser(cardUid)
            }

            // 情境 3: 卡片已被其他人註冊
            else -> {
                Log.w(TAG, "⚠️ 情境 3: 卡片已被其他人註冊")
                Log.w(TAG, "卡片持有者: '$userIdFromCard'")
                Log.w(TAG, "嘗試註冊者: '$currentUserId'")
                NfcResult.RegisteredToAnotherUser(cardUid, userIdFromCard)
            }
        }
    }

    private fun authenticate(mifare: MifareClassic, sectorIndex: Int): Boolean {
        Log.d(TAG, "開始驗證 Sector $sectorIndex...")

        for ((index, key) in KNOWN_KEYS.withIndex()) {
            try {
                // 先嘗試 Key A
                if (mifare.authenticateSectorWithKeyA(sectorIndex, key)) {
                    Log.i(TAG, "✅ 驗證成功！Sector $sectorIndex, Key A: ${key.toHexString()}")
                    return true
                }
            } catch (e: IOException) {
                // 繼續嘗試下一個
            }
        }

        Log.e(TAG, "❌ Sector $sectorIndex 驗證失敗")
        return false
    }

    private fun readUserIdFromCard(tag: Tag): String? {
        val mifare = MifareClassic.get(tag) ?: return null
        try {
            mifare.connect()
            if (authenticate(mifare, SECTOR_INDEX)) {
                val blockData = mifare.readBlock(BLOCK_INDEX)

                val endIndex = blockData.indexOfFirst { it == 0.toByte() }
                val actualData = if (endIndex >= 0) {
                    blockData.copyOfRange(0, endIndex)
                } else {
                    blockData
                }

                val rawString = String(actualData, Charset.forName("UTF-8"))
                val cleanString = rawString
                    .filter { it.isLetterOrDigit() || it in ".-_@" }
                    .trim()

                Log.d(TAG, "[讀取] Block $BLOCK_INDEX 原始 hex: ${blockData.toHexString()}")
                Log.d(TAG, "[讀取] 解析字串: '$cleanString'")

                return if (cleanString.isNotEmpty()) cleanString else null
            }
        } catch (e: Exception) {
            Log.e(TAG, "❌ [Read] 錯誤: ${e.message}", e)
        } finally {
            if (mifare.isConnected) mifare.close()
        }
        return null
    }

    private fun writeUserIdToCard(tag: Tag, userId: String): Boolean {
        Log.d(TAG, "========== 寫入流程 ==========")
        Log.d(TAG, "目標 User ID: '$userId'")

        val mifare = MifareClassic.get(tag)
        if (mifare == null) {
            Log.e(TAG, "❌ 無法取得 MifareClassic")
            return false
        }

        try {
            mifare.connect()
            Log.d(TAG, "✅ 已連線")
            Log.d(TAG, "卡片類型: ${mifare.type}")
            Log.d(TAG, "Sector 數: ${mifare.sectorCount}")
            Log.d(TAG, "目標位置: Sector $SECTOR_INDEX, Block $BLOCK_INDEX")

            if (!authenticate(mifare, SECTOR_INDEX)) {
                Log.e(TAG, "❌ 驗證失敗")
                return false
            }

            // ✅ 讀取寫入前的狀態
            val beforeData = mifare.readBlock(BLOCK_INDEX)
            Log.d(TAG, "[寫入前] Block $BLOCK_INDEX: ${beforeData.toHexString()}")

            // ✅ 準備資料
            val userIdBytes = userId.toByteArray(Charset.forName("UTF-8"))
            if (userIdBytes.size > 16) {
                Log.e(TAG, "❌ User ID 太長: ${userIdBytes.size} bytes")
                return false
            }

            val blockData = ByteArray(16) { 0x00 }
            System.arraycopy(userIdBytes, 0, blockData, 0, userIdBytes.size)
            Log.d(TAG, "[準備寫入] ${blockData.toHexString()}")

            // ✅ 執行寫入
            try {
                mifare.writeBlock(BLOCK_INDEX, blockData)
                Log.d(TAG, "✅ writeBlock() 執行完成")
            } catch (e: IOException) {
                Log.e(TAG, "❌ writeBlock() 拋出異常: ${e.message}", e)

                // ✅✅✅ 嘗試其他 Block
                Log.w(TAG, "⚠️ Block $BLOCK_INDEX 寫入失敗，嘗試 Block 4...")
                try {
                    mifare.writeBlock(4, blockData)
                    Log.d(TAG, "✅ Block 4 寫入成功！更新常數...")
                    // 注意：這裡只是測試，實際使用要修改 BLOCK_INDEX 常數
                    return verifyWrite(mifare, 4, userId)
                } catch (e2: IOException) {
                    Log.e(TAG, "❌ Block 4 也失敗: ${e2.message}")
                    return false
                }
            }

            Thread.sleep(100)

            // ✅ 驗證寫入
            return verifyWrite(mifare, BLOCK_INDEX, userId)

        } catch (e: Exception) {
            Log.e(TAG, "❌ 寫入異常: ${e.message}", e)
            return false
        } finally {
            if (mifare.isConnected) {
                mifare.close()
                Log.d(TAG, "連線已關閉")
            }
        }
    }

    private fun verifyWrite(mifare: MifareClassic, blockIndex: Int, expectedUserId: String): Boolean {
        val afterData = mifare.readBlock(blockIndex)
        Log.d(TAG, "[寫入後] Block $blockIndex: ${afterData.toHexString()}")

        val endIndex = afterData.indexOfFirst { it == 0.toByte() }
        val actualData = if (endIndex >= 0) {
            afterData.copyOfRange(0, endIndex)
        } else {
            afterData
        }
        val verifyString = String(actualData, Charset.forName("UTF-8")).trim()

        val isMatch = verifyString == expectedUserId
        Log.d(TAG, "[驗證] 預期: '$expectedUserId'")
        Log.d(TAG, "[驗證] 實際: '$verifyString'")
        Log.d(TAG, "[驗證] 結果: ${if (isMatch) "✅ 成功" else "❌ 失敗"}")

        return isMatch
    }

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