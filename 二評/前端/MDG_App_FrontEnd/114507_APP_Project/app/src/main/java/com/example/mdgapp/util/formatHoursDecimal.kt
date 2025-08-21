package com.example.mdgapp.util

fun formatHoursDecimal(seconds: Int): String {
    val hours = seconds / 3600f
    return String.format("%.1f hr", hours)
}
