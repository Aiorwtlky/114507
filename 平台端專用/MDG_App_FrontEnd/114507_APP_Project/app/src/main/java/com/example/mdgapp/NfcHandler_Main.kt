package com.example.mdgapp
/*
import android.content.Context
import android.content.Intent
import android.nfc.NdefMessage
import android.nfc.NdefRecord
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.MifareClassic
import android.nfc.tech.Ndef
import android.nfc.tech.NdefFormatable
import android.util.Log
import com.example.mdgapp.data.model.UserProfile
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.io.IOException
import java.nio.charset.Charset

class NfcHandler_Main(private val context: Context) {

    private val TAG = "NfcHandler"

    // ⭐ WriteSuccess 現在會回傳卡片序號，用於後續 API 綁定
    sealed class NfcResult {
        data class ReadSuccess(val userProfile: UserProfile) : NfcResult()
        data class WriteSuccess(val serialNumber: String, val writtenData: String) : NfcResult()
        data class Error(val message: String) : NfcResult()
    }

    // ⭐ 智慧型讀取：優先 NDEF，失敗則嘗試 Mifare Classic
    fun readUserProfile(intent: Intent): NfcResult {
        val tag: Tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG) ?: return NfcResult.Error("找不到 Tag")

        // 優先嘗試 NDEF 標準讀取
        val ndef = Ndef.get(tag)
        if (ndef != null) {
            Log.d(TAG, "[Read] 卡片支援 NDEF，嘗試 NDEF 讀取...")
            try {
                ndef.connect()
                // 優先使用緩存訊息，避免重複 IO 操作
                val ndefMessage = ndef.cachedNdefMessage ?: ndef.ndefMessage
                val jsonString = getTextFromNdefMessage(ndefMessage)
                ndef.close()
                if (jsonString.isNotEmpty()) {
                    Log.i(TAG, "[Read] NDEF 讀取成功。")
                    val userProfile = Json.decodeFromString<UserProfile>(jsonString)
                    return NfcResult.ReadSuccess(userProfile)
                } else {
                    Log.w(TAG, "[Read] NDEF 訊息為空，降級嘗試 Mifare Classic 讀取...")
                }
            } catch (e: Exception) {
                Log.w(TAG, "[Read] NDEF 讀取失敗: ${e.message}, 降級嘗試 Mifare Classic 讀取...")
                if (ndef.isConnected) ndef.close()
            }
        } else {
            Log.d(TAG, "[Read] 卡片不支援 NDEF，直接嘗試 Mifare Classic 讀取...")
        }

        // NDEF 讀取失敗或不支援，降級嘗試 Mifare Classic 讀取
        return readFromMifareClassic(tag)
    }

    // ⭐ 智慧型寫入：優先 NDEF，失敗則嘗試 Mifare Classic
    fun writeUserProfile(tag: Tag, userProfile: UserProfile): NfcResult {
        val serialNumber = tag.id.toHexString()
        val jsonData = Json.encodeToString(userProfile)
        val dataSize = jsonData.toByteArray().size

        // 優先嘗試 NDEF 標準寫入
        try {
            val message = createNdefMessage(jsonData)

            // 情況 1：卡片已支援 NDEF
            val ndef = Ndef.get(tag)
            if (ndef != null) {
                Log.d(TAG, "[Write] 卡片已支援 NDEF，嘗試 NDEF 寫入...")
                ndef.connect()
                if (!ndef.isWritable) {
                    Log.e(TAG, "[Write] NDEF 寫入失敗: 卡片是唯讀的。")
                    ndef.close()
                    return NfcResult.Error("卡片是唯讀的")
                }
                if (ndef.maxSize < dataSize) {
                    Log.e(TAG, "[Write] NDEF 寫入失敗: 資料太大(${dataSize} bytes)，卡片容量不足(${ndef.maxSize} bytes)。")
                    ndef.close()
                    return NfcResult.Error("資料太大，卡片容量不足")
                }
                ndef.writeNdefMessage(message)
                ndef.close()
                Log.i(TAG, "[Write] NDEF 寫入成功。")
                return NfcResult.WriteSuccess(serialNumber, jsonData)
            }

            // 情況 2：卡片可被格式化為 NDEF
            val ndefFormatable = NdefFormatable.get(tag)
            if (ndefFormatable != null) {
                Log.d(TAG, "[Write] 卡片可被格式化為 NDEF，嘗試格式化並寫入...")
                ndefFormatable.connect()
                ndefFormatable.format(message)
                ndefFormatable.close()
                Log.i(TAG, "[Write] NDEF 格式化並寫入成功。")
                return NfcResult.WriteSuccess(serialNumber, "(格式化後首次寫入)")
            }
        } catch (e: Exception) {
            Log.w(TAG, "[Write] NDEF 寫入/格式化失敗: ${e.message}, 降級嘗試 Mifare Classic 寫入...")
        }

        // NDEF 寫入失敗，降級嘗試 Mifare Classic 寫入
        Log.d(TAG, "[Write] NDEF 流程失敗，降級嘗試 Mifare Classic 寫入...")
        return writeToMifareClassic(tag, serialNumber, jsonData)
    }

    private fun createNdefMessage(text: String): NdefMessage {
        // 建立一個包含 UTF-8 文字的 NDEF 記錄
        val record = NdefRecord.createTextRecord("en", text)
        return NdefMessage(arrayOf(record))
    }

    private fun getTextFromNdefMessage(message: NdefMessage?): String {
        if (message == null) return ""
        val builder = StringBuilder()
        message.records.forEach { record ->
            // 確認是標準的文字記錄
            if (record.tnf == NdefRecord.TNF_WELL_KNOWN && record.type.contentEquals(NdefRecord.RTD_TEXT)) {
                try {
                    val payload = record.payload
                    // 根據狀態字節確定文字編碼 (UTF-8/UTF-16)
                    val textEncoding = if ((payload[0].toInt() and 128) == 0) "UTF-8" else "UTF-16"
                    // 取得語言碼長度
                    val languageCodeLength = payload[0].toInt() and 63
                    // 解碼
                    builder.append(
                        String(
                            payload,
                            languageCodeLength + 1,
                            payload.size - languageCodeLength - 1,
                            Charset.forName(textEncoding)
                        )
                    )
                } catch (e: Exception) {
                    Log.e(TAG, "解析 NDEF Record 失敗: ${e.message}")
                }
            }
        }
        return builder.toString()
    }

    // --- 以下為 Mifare Classic 專用方法 ---

    private fun writeToMifareClassic(tag: Tag, serialNumber: String, jsonData: String): NfcResult {
        val mifare = MifareClassic.get(tag) ?: return NfcResult.Error("卡片不支援 NDEF 也不是 Mifare Classic")
        Log.d(TAG, "[Write-MC] 正在執行 Mifare Classic 寫入...")
        try {
            mifare.connect()
            // 寫入前先洗白
            Log.d(TAG, "[Write-MC] 正在清空卡片舊資料...")
            if (!wipeMifareCard(mifare)) {
                Log.e(TAG, "[Write-MC] 清空卡片失敗。")
                return NfcResult.Error("清空卡片失敗")
            }

            val jsonDataBytes = jsonData.toByteArray(Charset.forName("UTF-8"))
            if (jsonDataBytes.size > mifare.size) {
                Log.e(TAG, "[Write-MC] 資料太大(${jsonDataBytes.size} bytes)，超過卡片容量(${mifare.size} bytes)。")
                return NfcResult.Error("資料太大(${jsonDataBytes.size} bytes)")
            }

            var bytesWritten = 0
            // 從 Sector 1 開始寫入，避開通常包含廠商資訊的 Sector 0
            for (sectorIndex in 1 until mifare.sectorCount) {
                if (bytesWritten >= jsonDataBytes.size) break
                // 使用預設金鑰 A 進行認證
                if (mifare.authenticateSectorWithKeyA(sectorIndex, MifareClassic.KEY_DEFAULT)) {
                    // 每個 Sector 的最後一個 block 是 Trailer Block，不可寫入使用者資料
                    for (blockInSector in 0 until mifare.getBlockCountInSector(sectorIndex) - 1) {
                        if (bytesWritten >= jsonDataBytes.size) break
                        val blockIndex = mifare.sectorToBlock(sectorIndex) + blockInSector
                        val chunk = jsonDataBytes.drop(bytesWritten).take(16).toByteArray()
                        val blockData = ByteArray(16) { 0 } // 建立一個 16 bytes 的空 block
                        chunk.copyInto(blockData) // 將資料複製進去，不足的部分會是 0
                        mifare.writeBlock(blockIndex, blockData)
                        bytesWritten += 16
                    }
                } else {
                    Log.e(TAG, "[Write-MC] 寫入失敗: Sector $sectorIndex 認證失敗。")
                    return NfcResult.Error("寫入失敗: Sector $sectorIndex 認證失敗")
                }
            }
            Log.i(TAG, "[Write-MC] Mifare Classic 寫入成功，共寫入 $bytesWritten bytes。")
            return NfcResult.WriteSuccess(serialNumber, jsonData)
        } catch (e: IOException) {
            Log.e(TAG, "[Write-MC] 寫入時發生 IO 異常: ${e.message}")
            return NfcResult.Error("寫入失敗: ${e.message}")
        } finally {
            if (mifare.isConnected) mifare.close()
        }
    }

    private fun readFromMifareClassic(tag: Tag): NfcResult {
        val mifare = MifareClassic.get(tag) ?: return NfcResult.Error("卡片不支援 NDEF 也不是 Mifare Classic")
        Log.d(TAG, "[Read-MC] 正在執行 Mifare Classic 讀取...")
        return try {
            mifare.connect()
            val dataBytes = mutableListOf<Byte>()
            // 從 Sector 1 開始讀取
            for (sectorIndex in 1 until mifare.sectorCount) {
                if (mifare.authenticateSectorWithKeyA(sectorIndex, MifareClassic.KEY_DEFAULT)) {
                    for (blockInSector in 0 until mifare.getBlockCountInSector(sectorIndex) - 1) {
                        val blockIndex = mifare.sectorToBlock(sectorIndex) + blockInSector
                        val blockData = mifare.readBlock(blockIndex)

                        // 尋找資料結束的 null 字元 (0x00)
                        val nullIndex = blockData.indexOf(0.toByte())
                        if (nullIndex != -1) {
                            // 如果找到，表示資料到此為止
                            dataBytes.addAll(blockData.take(nullIndex))
                            val jsonString = String(dataBytes.toByteArray(), Charset.forName("UTF-8"))
                            Log.i(TAG, "[Read-MC] Mifare Classic 讀取成功，在 block $blockIndex 找到結束符號。")
                            return NfcResult.ReadSuccess(Json.decodeFromString(jsonString))
                        } else {
                            // 沒找到，繼續加入整個 block 的資料
                            dataBytes.addAll(blockData.toList())
                        }
                    }
                }
            }
            // 如果所有 Sector 都讀完還沒找到結束符號，可能卡片有問題或格式不對
            Log.w(TAG, "[Read-MC] 讀取完畢，但在卡片中未找到有效資料的結束符號。")
            return NfcResult.Error("在卡片中未找到有效資料")
        } catch (e: Exception) {
            Log.e(TAG, "[Read-MC] 讀取時發生異常: ${e.message}")
            return NfcResult.Error("讀取失敗: ${e.message}")
        } finally {
            if (mifare.isConnected) mifare.close()
        }
    }

    private fun wipeMifareCard(mifare: MifareClassic): Boolean {
        try {
            val emptyBlock = ByteArray(16) { 0 }
            for (sectorIndex in 1 until mifare.sectorCount) {
                if (mifare.authenticateSectorWithKeyA(sectorIndex, MifareClassic.KEY_DEFAULT)) {
                    for (blockInSector in 0 until mifare.getBlockCountInSector(sectorIndex) - 1) {
                        mifare.writeBlock(mifare.sectorToBlock(sectorIndex) + blockInSector, emptyBlock)
                    }
                } else {
                    // 如果某個 sector 認證失敗，可能它有不同的 key，但對於「洗白」來說，我們只處理能用預設 key 打開的
                    Log.w(TAG, "[Wipe] Sector $sectorIndex 認證失敗，跳過。")
                }
            }
            return true
        } catch (e: IOException) {
            Log.e(TAG, "[Wipe] 清空卡片時發生 IO 異常: ${e.message}")
            return false
        }
    }

    // 將 ByteArray 轉換為 Hex 字串的輔助函式
    private fun ByteArray.toHexString(): String = joinToString("") { "%02X".format(it) }
}*/