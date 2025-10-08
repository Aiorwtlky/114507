// com.example.mdgapp.util.TimeUtils.kt
package com.example.mdgapp.util

fun formatTime(totalMinutes: Int): String {
    val hours = totalMinutes / 60
    val minutes = totalMinutes % 60
    return if (hours > 0) "%d:%02d".format(hours, minutes) else "$minutes 分"
}
