package com.example.mdgapp.data

import android.location.Location
import com.google.android.gms.maps.model.LatLng
import kotlin.random.Random

/**
 * 模擬行駛軌跡服務：從善導寺到台北車站的路徑
 * 路線依據 Google Maps 實際道路 (忠孝東路/忠孝西路) 精確模擬
 */
class SimulatedLocationService {

    // 善導寺到台北車站的實際行車路線座標
    // 基於 Google Maps 實際道路：忠孝東路一段 → 忠孝西路一段（最直接路線）
    private val shandaosiToTaipeiMain = listOf(
        // 起點：善導寺站 (忠孝東路一段 & 林森南路)
        LatLng(25.044565, 121.523285),

        // 沿忠孝東路一段往西
        LatLng(25.044680, 121.522800),
        LatLng(25.044795, 121.522315),
        LatLng(25.044910, 121.521830),
        LatLng(25.045025, 121.521345),
        LatLng(25.045140, 121.520860),
        LatLng(25.045255, 121.520375),
        LatLng(25.045370, 121.519890),
        LatLng(25.045485, 121.519405),

        // 進入忠孝西路一段
        LatLng(25.045600, 121.518920),
        LatLng(25.045715, 121.518435),
        LatLng(25.045830, 121.517950),
        LatLng(25.045945, 121.517465),
        LatLng(25.046060, 121.516980),
        LatLng(25.046175, 121.516495),
        LatLng(25.046290, 121.516010),

        // 抵達台北車站區域
        LatLng(25.046405, 121.515525),
        LatLng(25.046520, 121.515040),
        LatLng(25.046635, 121.514555),

        // 終點：台北車站
        LatLng(25.046750, 121.514070)
    )

    // 總時間設定（秒）- 實際騎車/開車約 3-5 分鐘
    private val simulatedTimeInSeconds = 180 // 3 分鐘

    /**
     * 生成完整的模擬路徑，包含精確的時間和距離計算
     * @return 模擬的 Location 列表
     */
    fun getFullSimulatedPath(): List<Location> {
        val path = mutableListOf<Location>()
        val totalPoints = shandaosiToTaipeiMain.size
        var currentTime = System.currentTimeMillis()

        // 計算每個點之間的時間間隔（毫秒）
        val timeIntervalMs = (simulatedTimeInSeconds * 1000) / (totalPoints - 1)

        shandaosiToTaipeiMain.forEachIndexed { index, latLng ->
            // 添加輕微的 GPS 誤差模擬（±2 公尺左右）
            val latOffset = Random.nextDouble(-0.00002, 0.00002)
            val lngOffset = Random.nextDouble(-0.00002, 0.00002)

            val simulatedLocation = Location("SimulatedProvider").apply {
                latitude = latLng.latitude + latOffset
                longitude = latLng.longitude + lngOffset
                time = currentTime

                // 設定速度和方位角（行駛方向）
                if (index > 0) {
                    val prevLoc = path[index - 1]
                    val distance = distanceTo(prevLoc)
                    val timeSeconds = timeIntervalMs / 1000f
                    speed = if (timeSeconds > 0) distance / timeSeconds else 0f
                    bearing = prevLoc.bearingTo(this)
                }

                // 設定精度
                accuracy = Random.nextFloat() * 5 + 5 // 5-10 公尺的精度
            }

            path.add(simulatedLocation)
            currentTime += timeIntervalMs
        }

        return path
    }

    /**
     * 提供更平滑的模擬路線（在原路徑點之間插值）
     * @param smoothFactor 平滑係數，建議 2-5，數值越大點越密集
     * @return 平滑處理後的 Location 列表
     */
    fun getSmoothSimulatedPath(smoothFactor: Int = 3): List<Location> {
        val path = mutableListOf<Location>()
        val totalSegments = shandaosiToTaipeiMain.size - 1
        var currentTime = System.currentTimeMillis()

        // 計算總點數和時間間隔
        val totalPoints = totalSegments * smoothFactor + 1
        val timeIntervalMs = (simulatedTimeInSeconds * 1000) / (totalPoints - 1)

        for (i in 0 until totalSegments) {
            val start = shandaosiToTaipeiMain[i]
            val end = shandaosiToTaipeiMain[i + 1]

            // 在每兩個點之間插值
            for (j in 0..smoothFactor) {
                // 最後一段的最後一個點跳過（會在下一段的起點處理）
                if (i == totalSegments - 1 && j == smoothFactor) continue

                val fraction = j / smoothFactor.toFloat()

                // 線性插值
                val lat = start.latitude + (end.latitude - start.latitude) * fraction
                val lng = start.longitude + (end.longitude - start.longitude) * fraction

                // 添加 GPS 誤差
                val latOffset = Random.nextDouble(-0.00002, 0.00002)
                val lngOffset = Random.nextDouble(-0.00002, 0.00002)

                val simulatedLocation = Location("SimulatedProvider").apply {
                    latitude = lat + latOffset
                    longitude = lng + lngOffset
                    time = currentTime

                    // 計算速度和方位角
                    if (path.isNotEmpty()) {
                        val prevLoc = path.last()
                        val distance = distanceTo(prevLoc)
                        val timeSeconds = timeIntervalMs / 1000f
                        speed = if (timeSeconds > 0) distance / timeSeconds else 0f
                        bearing = prevLoc.bearingTo(this)
                    }

                    accuracy = Random.nextFloat() * 5 + 5
                }

                path.add(simulatedLocation)
                currentTime += timeIntervalMs
            }
        }

        // 添加終點
        val lastPoint = shandaosiToTaipeiMain.last()
        val finalLocation = Location("SimulatedProvider").apply {
            latitude = lastPoint.latitude + Random.nextDouble(-0.00002, 0.00002)
            longitude = lastPoint.longitude + Random.nextDouble(-0.00002, 0.00002)
            time = currentTime

            // 計算最後一點的速度和方位角
            if (path.isNotEmpty()) {
                val prevLoc = path.last()
                val distance = distanceTo(prevLoc)
                val timeSeconds = timeIntervalMs / 1000f
                speed = if (timeSeconds > 0) distance / timeSeconds else 0f
                bearing = prevLoc.bearingTo(this)
            }

            accuracy = Random.nextFloat() * 5 + 5
        }
        path.add(finalLocation)

        return path
    }

    /**
     * 取得原始路徑點（用於地圖顯示）
     */
    fun getSimulatedSnappedRoute(): List<LatLng> {
        return shandaosiToTaipeiMain
    }

    /**
     * 計算路徑總距離（公尺）
     */
    fun getTotalDistance(): Float {
        var totalDistance = 0f
        for (i in 1 until shandaosiToTaipeiMain.size) {
            val start = Location("").apply {
                latitude = shandaosiToTaipeiMain[i - 1].latitude
                longitude = shandaosiToTaipeiMain[i - 1].longitude
            }
            val end = Location("").apply {
                latitude = shandaosiToTaipeiMain[i].latitude
                longitude = shandaosiToTaipeiMain[i].longitude
            }
            totalDistance += start.distanceTo(end)
        }
        return totalDistance
    }

    /**
     * 取得預估行駛時間（秒）
     */
    fun getEstimatedTime(): Int {
        return simulatedTimeInSeconds
    }
}