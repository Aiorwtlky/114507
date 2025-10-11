package com.example.mdgapp

import android.nfc.NdefMessage
import android.nfc.NdefRecord
import android.nfc.Tag
import android.nfc.tech.Ndef
import android.nfc.tech.NdefFormatable
import android.util.Log
import java.io.IOException
import java.nio.charset.Charset

class NfcHandler(private val activity: MainActivity) {

    private val TAG = "NfcHandler"

    sealed class NfcResult {
        data class WriteSuccess(
            val driverId: String,
            val serialNumber: String,
            val isNewCard: Boolean // 是否為新卡片
        ) : NfcResult()

        data class UpdateSuccess(
            val oldDriverId: String,
            val newDriverId: String,
            val serialNumber: String
        ) : NfcResult()

        data class AlreadyRegistered(
            val driverId: String,
            val serialNumber: String
        ) : NfcResult()

        data class ReadSuccess(val serialNumber: String) : NfcResult()
        data class Error(val message: String) : NfcResult()
    }

    /**
     * 讀取卡片資料並判斷註冊狀態
     * @param tag NFC 標籤
     * @param currentDriverId 當前使用者的人員編號
     * @return NfcResult 包含操作結果
     */
    fun handleCardRegistration(tag: Tag, currentDriverId: String): NfcResult {
        val cardSerialNumber = tag.id.toHexString()
        Log.d(TAG, "偵測到卡片實體編號: $cardSerialNumber")
        Log.d(TAG, "當前使用者人員編號: $currentDriverId")

        return try {
            // 嘗試讀取卡片上的資料
            val storedDriverId = readDriverIdFromCard(tag)

            when {
                // 情境 1: 卡片未寫入任何資料（首次註冊）
                storedDriverId == null -> {
                    Log.i(TAG, "情境 1: 卡片未註冊，開始寫入人員編號")
                    writeDriverIdToCard(tag, currentDriverId, cardSerialNumber, isNewCard = true)
                }

                // 情境 3: 卡片已註冊且人員編號相同（已註冊）
                storedDriverId == currentDriverId -> {
                    Log.i(TAG, "情境 3: 卡片已註冊給當前使用者")
                    NfcResult.AlreadyRegistered(
                        driverId = currentDriverId,
                        serialNumber = cardSerialNumber
                    )
                }

                // 情境 2: 卡片已註冊但人員編號不同（更新註冊）
                else -> {
                    Log.i(TAG, "情境 2: 卡片已註冊給其他使用者，開始更新")
                    Log.i(TAG, "舊人員編號: $storedDriverId, 新人員編號: $currentDriverId")

                    val writeResult = writeDriverIdToCard(
                        tag,
                        currentDriverId,
                        cardSerialNumber,
                        isNewCard = false
                    )

                    // 轉換為 UpdateSuccess
                    if (writeResult is NfcResult.WriteSuccess) {
                        NfcResult.UpdateSuccess(
                            oldDriverId = storedDriverId,
                            newDriverId = currentDriverId,
                            serialNumber = cardSerialNumber
                        )
                    } else {
                        writeResult
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "處理卡片註冊時發生錯誤", e)
            NfcResult.Error("讀取卡片失敗: ${e.message}")
        }
    }

    /**
     * 從卡片讀取人員編號
     * @return 人員編號，如果卡片未寫入資料則返回 null
     */
    private fun readDriverIdFromCard(tag: Tag): String? {
        var ndef: Ndef? = null

        try {
            ndef = Ndef.get(tag)

            if (ndef == null) {
                Log.d(TAG, "卡片不支援 NDEF 格式或尚未格式化")
                return null
            }

            ndef.connect()
            val ndefMessage = ndef.cachedNdefMessage

            if (ndefMessage == null) {
                Log.d(TAG, "卡片為空白，未寫入任何資料")
                return null
            }

            val records = ndefMessage.records
            if (records.isEmpty()) {
                Log.d(TAG, "卡片無記錄")
                return null
            }

            // 讀取第一筆記錄
            val record = records[0]
            val payload = record.payload

            if (payload.isEmpty()) {
                Log.d(TAG, "記錄為空")
                return null
            }

            // 跳過語言碼（第一個位元組）
            val textEncoding = if ((payload[0].toInt() and 128) == 0) "UTF-8" else "UTF-16"
            val languageCodeLength = payload[0].toInt() and 63

            val text = String(
                payload,
                languageCodeLength + 1,
                payload.size - languageCodeLength - 1,
                Charset.forName(textEncoding)
            )

            Log.d(TAG, "從卡片讀取到人員編號: $text")
            return text

        } catch (e: Exception) {
            Log.e(TAG, "讀取卡片資料時發生錯誤", e)
            return null
        } finally {
            try {
                ndef?.close()
            } catch (e: IOException) {
                Log.e(TAG, "關閉 NDEF 連線時發生錯誤", e)
            }
        }
    }

    /**
     * 將人員編號寫入卡片
     */
    private fun writeDriverIdToCard(
        tag: Tag,
        driverId: String,
        cardSerialNumber: String,
        isNewCard: Boolean
    ): NfcResult {
        var ndef: Ndef? = null
        var ndefFormatable: NdefFormatable? = null

        try {
            // 建立 NDEF 訊息
            val message = createNdefMessage(driverId)

            // 嘗試使用 Ndef 技術
            ndef = Ndef.get(tag)

            if (ndef != null) {
                ndef.connect()

                if (!ndef.isWritable) {
                    Log.e(TAG, "卡片不可寫入")
                    return NfcResult.Error("卡片為唯讀，無法寫入")
                }

                val size = message.toByteArray().size
                if (ndef.maxSize < size) {
                    Log.e(TAG, "卡片容量不足")
                    return NfcResult.Error("卡片容量不足，無法寫入")
                }

                ndef.writeNdefMessage(message)
                Log.i(TAG, "成功寫入人員編號: $driverId")

                return NfcResult.WriteSuccess(
                    driverId = driverId,
                    serialNumber = cardSerialNumber,
                    isNewCard = isNewCard
                )

            } else {
                // 卡片尚未格式化，嘗試格式化
                ndefFormatable = NdefFormatable.get(tag)

                if (ndefFormatable != null) {
                    ndefFormatable.connect()
                    ndefFormatable.format(message)
                    Log.i(TAG, "卡片格式化並寫入人員編號: $driverId")

                    return NfcResult.WriteSuccess(
                        driverId = driverId,
                        serialNumber = cardSerialNumber,
                        isNewCard = true
                    )
                } else {
                    Log.e(TAG, "卡片不支援 NDEF 格式")
                    return NfcResult.Error("卡片不支援 NDEF 格式")
                }
            }

        } catch (e: Exception) {
            Log.e(TAG, "寫入卡片時發生錯誤", e)
            return NfcResult.Error("寫入失敗: ${e.message}")
        } finally {
            try {
                ndef?.close()
                ndefFormatable?.close()
            } catch (e: IOException) {
                Log.e(TAG, "關閉連線時發生錯誤", e)
            }
        }
    }

    /**
     * 建立 NDEF 訊息
     */
    private fun createNdefMessage(text: String): NdefMessage {
        val langBytes = "en".toByteArray(Charset.forName("US-ASCII"))
        val textBytes = text.toByteArray(Charset.forName("UTF-8"))

        val textLength = textBytes.size
        val langLength = langBytes.size

        val payload = ByteArray(1 + langLength + textLength)
        payload[0] = langLength.toByte()

        System.arraycopy(langBytes, 0, payload, 1, langLength)
        System.arraycopy(textBytes, 0, payload, 1 + langLength, textLength)

        val record = NdefRecord(
            NdefRecord.TNF_WELL_KNOWN,
            NdefRecord.RTD_TEXT,
            ByteArray(0),
            payload
        )

        return NdefMessage(arrayOf(record))
    }

    /**
     * 僅讀取卡片實體編號（用於打卡功能）
     */
    fun readCardSerialNumber(tag: Tag): NfcResult {
        val cardSerialNumber = tag.id.toHexString()
        Log.i(TAG, "讀取到卡片實體編號: $cardSerialNumber")
        return NfcResult.ReadSuccess(cardSerialNumber)
    }

    /**
     * 將 ByteArray 轉換為十六進位字串
     */
    private fun ByteArray.toHexString(): String =
        joinToString("") { "%02X".format(it) }
}