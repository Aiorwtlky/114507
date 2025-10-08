package com.example.mdgapp

import android.content.Context
import android.content.Intent
import android.nfc.NdefMessage
import android.nfc.NdefRecord
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.Ndef
import android.nfc.tech.NdefFormatable
import android.util.Log
import com.example.mdgapp.data.model.UserProfile
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.nio.charset.Charset

class NfcHandler(private val context: Context) {

    sealed class NfcResult {
        data class ReadSuccess(val userProfile: UserProfile) : NfcResult()
        data class WriteSuccess(val writtenData: String, val readBackData: String) : NfcResult()
        data class Error(val message: String) : NfcResult()
    }

    fun readUserProfile(intent: Intent): NfcResult {
        return try {
            val rawMessages = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES)
            if (rawMessages.isNullOrEmpty()) {
                return NfcResult.Error("卡片中沒有 NDEF 資料")
            }

            val messages = rawMessages.map { it as NdefMessage }
            val jsonString = getTextFromNdefMessages(messages)

            if (jsonString.isNotEmpty()) {
                val userProfile = Json.decodeFromString<UserProfile>(jsonString)
                NfcResult.ReadSuccess(userProfile)
            } else {
                NfcResult.Error("卡片內無有效資料")
            }
        } catch (t: Throwable) { // ⭐ 修改處：捕捉更廣泛的 Throwable
            Log.e("NfcHandler", "讀取或解析 UserProfile 失敗", t)
            NfcResult.Error("讀取或解析失敗: ${t.message}")
        }
    }

    fun writeUserProfile(tag: Tag, userProfile: UserProfile): NfcResult {
        try {
            Log.d("NfcHandler", "開始序列化 UserProfile...")
            val jsonData = Json.encodeToString(userProfile)
            Log.d("NfcHandler", "序列化成功，準備建立 NDEF Message...")
            val message = createNdefMessage(jsonData)

            val ndef = Ndef.get(tag)
            if (ndef != null) {
                ndef.connect()
                if (!ndef.isWritable) return NfcResult.Error("卡片是唯讀的")
                if (ndef.maxSize < message.toByteArray().size) return NfcResult.Error("資料太大，卡片容量不足")

                ndef.writeNdefMessage(message)
                ndef.close()

                val readBackData = getTextFromNdefMessages(listOf(ndef.cachedNdefMessage))
                return NfcResult.WriteSuccess(jsonData, readBackData)
            }

            val ndefFormatable = NdefFormatable.get(tag)
            if (ndefFormatable != null) {
                ndefFormatable.connect()
                ndefFormatable.format(message)
                ndefFormatable.close()
                return NfcResult.WriteSuccess(jsonData, " (格式化後首次寫入，請重新掃描以讀取)")
            }

            return NfcResult.Error("這張卡片不支援 NDEF 格式化")

        } catch (t: Throwable) { // ⭐ 修改處：捕捉更廣泛的 Throwable
            Log.e("NfcHandler", "寫入 UserProfile 過程中發生嚴重錯誤", t)
            return NfcResult.Error("寫入失敗: ${t.javaClass.simpleName} - ${t.message}")
        }
    }

    private fun getTextFromNdefMessages(messages: List<NdefMessage>): String {
        val builder = StringBuilder()
        messages.forEach { message ->
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
        }
        return builder.toString()
    }

    private fun createNdefMessage(text: String): NdefMessage {
        val record = NdefRecord.createTextRecord("en", text)
        return NdefMessage(arrayOf(record))
    }
}