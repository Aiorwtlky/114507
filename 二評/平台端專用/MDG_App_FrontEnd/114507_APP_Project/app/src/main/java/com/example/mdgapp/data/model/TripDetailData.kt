// 檔案路徑: app/src/main/java/com/example/mdgapp/data/model/TripDetailData.kt
package com.example.mdgapp.data.model

import com.google.gson.annotations.SerializedName

// 對應整個 API 回應的最外層物件
data class TripDetail(
    val id: Int,
    @SerializedName("trip_number")
    val tripNumber: String,
    val name: String,
    val score: String,
    @SerializedName("ai_suggestion")
    val aiSuggestion: String,
    @SerializedName("start_time")
    val startTime: String,
    @SerializedName("end_time")
    val endTime: String?,
    val personnel: Personnel,
    val group: Group,
    val device: Device,
    @SerializedName("aivisionlog_set")
    val aiVisionLogSet: List<AiVisionLog>,
    @SerializedName("videorecord_set")
    val videoRecordSet: List<VideoRecord>
)

// 對應 API 回應中的巢狀物件
data class Personnel(
    val id: Int,
    val username: String
)

data class Group(
    val id: Int,
    val name: String
)

data class Device(
    val id: Int,
    @SerializedName("device_number")
    val deviceNumber: String
)

data class AiVisionLog(
    val timestamp: String,
    @SerializedName("event_details")
    val eventDetails: String,
    @SerializedName("confidence_score")
    val confidenceScore: Float,
    val event: AiEvent
)

data class AiEvent(
    @SerializedName("event_number")
    val eventNumber: String,
    val description: String,
    @SerializedName("deduction_points")
    val deductionPoints: Int
)

data class VideoRecord(
    @SerializedName("video_number")
    val videoNumber: String,
    @SerializedName("start_time")
    val startTime: String,
    @SerializedName("end_time")
    val endTime: String,
    val location: String // Video URL
)