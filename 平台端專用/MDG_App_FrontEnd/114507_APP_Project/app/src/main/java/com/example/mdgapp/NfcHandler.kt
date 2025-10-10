package com.example.mdgapp

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

class NfcHandler(private val context: Context) {

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
            try {
                ndef.connect()
                val ndefMessage = ndef.cachedNdefMessage ?: ndef.ndefMessage
                val jsonString = getTextFromNdefMessage(ndefMessage)
                ndef.close()
                if (jsonString.isNotEmpty()) {
                    val userProfile = Json.decodeFromString<UserProfile>(jsonString)
                    return NfcResult.ReadSuccess(userProfile)
                }
            } catch (e: Exception) {
                Log.w(TAG, "NDEF 讀取失敗: ${e.message}, 降級嘗試 Mifare Classic 讀取...")
                if (ndef.isConnected) ndef.close()
            }
        }

        // NDEF 讀取失敗，降級嘗試 Mifare Classic 讀取
        return readFromMifareClassic(tag)
    }

    // ⭐ 智慧型寫入：優先 NDEF，失敗則嘗試 Mifare Classic
    fun writeUserProfile(tag: Tag, userProfile: UserProfile): NfcResult {
        val serialNumber = tag.id.toHexString()
        val jsonData = Json.encodeToString(userProfile)

        // 優先嘗試 NDEF 標準寫入
        try {
            val message = createNdefMessage(jsonData)
            val ndef = Ndef.get(tag)
            if (ndef != null) {
                ndef.connect()
                if (!ndef.isWritable) return NfcResult.Error("卡片是唯讀的")
                if (ndef.maxSize < message.toByteArray().size) return NfcResult.Error("資料太大，卡片容量不足")
                ndef.writeNdefMessage(message)
                ndef.close()
                return NfcResult.WriteSuccess(serialNumber, jsonData)
            }

            val ndefFormatable = NdefFormatable.get(tag)
            if (ndefFormatable != null) {
                ndefFormatable.connect()
                ndefFormatable.format(message)
                ndefFormatable.close()
                return NfcResult.WriteSuccess(serialNumber, "(格式化後首次寫入)")
            }
        } catch (e: Exception) {
            Log.w(TAG, "NDEF 寫入失敗: ${e.message}, 降級嘗試 Mifare Classic 寫入...")
        }

        // NDEF 寫入失敗，降級嘗試 Mifare Classic 寫入
        return writeToMifareClassic(tag, serialNumber, jsonData)
    }

    private fun createNdefMessage(text: String): NdefMessage {
        val record = NdefRecord.createTextRecord("en", text)
        return NdefMessage(arrayOf(record))
    }

    private fun getTextFromNdefMessage(message: NdefMessage?): String {
        if (message == null) return ""
        val builder = StringBuilder()
        message.records.forEach { record ->
            if (record.tnf == NdefRecord.TNF_WELL_KNOWN && record.type.contentEquals(NdefRecord.RTD_TEXT)) {
                val payload = record.payload
                val textEncoding = if ((payload[0].toInt() and 128) == 0) "UTF-8" else "UTF-16"
                val languageCodeLength = payload[0].toInt() and 63
                builder.append(
                    String(
                        payload,
                        languageCodeLength + 1,
                        payload.size - languageCodeLength - 1,
                        Charset.forName(textEncoding)
                    )
                )
            }
        }
        return builder.toString()
    }

    // --- 以下為 Mifare Classic 專用方法 ---

    private fun writeToMifareClassic(tag: Tag, serialNumber: String, jsonData: String): NfcResult {
        val mifare = MifareClassic.get(tag) ?: return NfcResult.Error("卡片不支援 NDEF 也不是 Mifare Classic")
        try {
            mifare.connect()
            // 寫入前先洗白
            if (!wipeMifareCard(mifare)) return NfcResult.Error("洗白卡片失敗")

            val jsonDataBytes = jsonData.toByteArray(Charset.forName("UTF-8"))
            if (jsonDataBytes.size > mifare.size) return NfcResult.Error("資料太大(${jsonDataBytes.size} bytes)")

            var bytesWritten = 0
            for (sectorIndex in 1 until mifare.sectorCount) {
                if (bytesWritten >= jsonDataBytes.size) break
                if (mifare.authenticateSectorWithKeyA(sectorIndex, MifareClassic.KEY_DEFAULT)) {
                    for (blockInSector in 0 until mifare.getBlockCountInSector(sectorIndex) - 1) {
                        if (bytesWritten >= jsonDataBytes.size) break
                        val blockIndex = mifare.sectorToBlock(sectorIndex) + blockInSector
                        val chunk = jsonDataBytes.drop(bytesWritten).take(16).toByteArray()
                        val blockData = ByteArray(16) { 0 }
                        chunk.copyInto(blockData)
                        mifare.writeBlock(blockIndex, blockData)
                        bytesWritten += 16
                    }
                } else {
                    return NfcResult.Error("寫入失敗: Sector $sectorIndex 認證失敗")
                }
            }
            return NfcResult.WriteSuccess(serialNumber, jsonData)
        } catch (e: IOException) {
            return NfcResult.Error("寫入失敗: ${e.message}")
        } finally {
            if (mifare.isConnected) mifare.close()
        }
    }

    private fun readFromMifareClassic(tag: Tag): NfcResult {
        val mifare = MifareClassic.get(tag) ?: return NfcResult.Error("卡片不支援 NDEF 也不是 Mifare Classic")
        return try {
            mifare.connect()
            val dataBytes = mutableListOf<Byte>()
            for (sectorIndex in 1 until mifare.sectorCount) {
                if (mifare.authenticateSectorWithKeyA(sectorIndex, MifareClassic.KEY_DEFAULT)) {
                    for (blockInSector in 0 until mifare.getBlockCountInSector(sectorIndex) - 1) {
                        val blockIndex = mifare.sectorToBlock(sectorIndex) + blockInSector
                        val blockData = mifare.readBlock(blockIndex)
                        val nullIndex = blockData.indexOf(0.toByte())
                        if (nullIndex != -1) {
                            dataBytes.addAll(blockData.take(nullIndex))
                            val jsonString = String(dataBytes.toByteArray(), Charset.forName("UTF-8"))
                            return NfcResult.ReadSuccess(Json.decodeFromString(jsonString))
                        } else {
                            dataBytes.addAll(blockData.toList())
                        }
                    }
                }
            }
            return NfcResult.Error("在卡片中未找到有效資料")
        } catch (e: Exception) {
            NfcResult.Error("讀取失敗: ${e.message}")
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
                }
            }
            return true
        } catch (e: IOException) {
            return false
        }
    }

    private fun ByteArray.toHexString(): String = joinToString("") { "%02X".format(it) }
}