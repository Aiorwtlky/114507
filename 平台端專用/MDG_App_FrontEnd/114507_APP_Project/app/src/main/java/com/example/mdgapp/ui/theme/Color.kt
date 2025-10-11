// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/theme/Color.kt

package com.example.mdgapp.ui.theme

import androidx.compose.ui.graphics.Color

// 1. 定義新的淺色主題顏色
val AppBackgroundWhite = Color(0xFFFFFFFF)  // 背景使用的白色
val AppPrimaryBlue = Color(0xFF0D6EFD)     // 用於主要標題、邊框、按鈕的藍色
val AppTextBlack = Color(0xFF000000)       // 文字使用的黑色
val AppTextWhite = Color(0xFFFFFFFF)      // 用於藍色背景上的文字顏色
val AppSecondaryGrey = Color(0xFF6c757d)   // 次要文字或圖示的灰色

// 2. (可選) 保留原始的顏色以備不時之需
val Purple80 = Color(0xFFD0BCFF)
val PurpleGrey80 = Color(0xFFCCC2DC)
val Pink80 = Color(0xFFEFB8C8)

val Purple40 = Color(0xFF6650a4)
val PurpleGrey40 = Color(0xFF625b71)
val Pink40 = Color(0xFF7D5260)


// 3. 更新舊顏色名稱的向下相容指向
// 讓舊的 UI 畫面能繼續編譯，並指向新的淺色主題顏色。
val iOsBackground = AppBackgroundWhite
val iOsComponentBackground = AppBackgroundWhite
val iOsBlue = AppPrimaryBlue
val iOsTextPrimary = AppTextBlack
val iOsTextSecondary = AppSecondaryGrey
val iOsSeparator = AppSecondaryGrey // 分隔線使用灰色