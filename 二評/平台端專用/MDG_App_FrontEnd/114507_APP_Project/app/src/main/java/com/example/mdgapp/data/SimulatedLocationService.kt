// 檔案路徑: app/src/main/java/com/example/mdgapp/data/SimulatedLocationService.kt
package com.example.mdgapp.data

import android.location.Location
import com.google.android.gms.maps.model.LatLng
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class SimulatedLocationService {

    // 模擬一條從台北車站到台北101的路徑
    private val path = listOf(
        LatLng(25.047924, 121.517082), // 台北車站
        LatLng(25.046219, 121.522359),
        LatLng(25.044342, 121.528657),
        LatLng(25.042531, 121.534560), // 華山文創
        LatLng(25.040113, 121.540897),
        LatLng(25.037888, 121.547568),
        LatLng(25.035813, 121.554030), // 國父紀念館附近
        LatLng(25.033879, 121.560755),
        LatLng(25.033976, 121.564949)  // 台北101
    )

    val locationUpdates: Flow<Location> = flow {
        path.forEach { latLng ->
            val mockLocation = Location("Simulated").apply {
                latitude = latLng.latitude
                longitude = latLng.longitude
            }
            emit(mockLocation)
            delay(3000) // 每3秒發送一個新座標
        }
    }
}