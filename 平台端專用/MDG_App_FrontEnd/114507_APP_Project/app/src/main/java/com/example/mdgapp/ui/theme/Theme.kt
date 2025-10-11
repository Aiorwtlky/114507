// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/theme/Theme.kt

package com.example.mdgapp.ui.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// 1. 建立一個符合你需求的「淺色主題」色彩配置
//    這裡只使用我們在 Color.kt 中定義好的顏色
private val CustomLightColorScheme = lightColorScheme(
    primary = AppPrimaryBlue,            // 主要顏色: 用於重要標題、邊框、按鈕等
    onPrimary = AppTextWhite,            // 在主要顏色(藍色)上方的文字顏色

    background = AppBackgroundWhite,     // App 的主要背景顏色
    onBackground = AppTextBlack,         // 在背景(白色)上方的文字顏色

    surface = AppBackgroundWhite,        // 卡片、對話框等元件的表面顏色
    onSurface = AppTextBlack,            // 在表面(白色)上方的文字顏色

    secondary = AppSecondaryGrey,        // 次要顏色 (例如次要按鈕或標籤)
    onSecondary = AppTextWhite           // 在次要顏色上方的文字顏色
)

@Composable
fun MyApplicationTheme(
    // 2. 預設強制使用淺色主題，忽略手機系統的深色模式設定
    darkTheme: Boolean = false,
    content: @Composable () -> Unit
) {
    // 3. 直接指定使用我們上面定義好的 CustomLightColorScheme
    val colorScheme = CustomLightColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window

            // 4. 更新狀態列顏色以符合我們的設計
            // 將狀態列背景設定為白色
            window.statusBarColor = colorScheme.background.toArgb()

            // 讓狀態列的圖示(時間、電量、訊號)變成「深色」，才能在白色背景上被看見
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = true
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography, // Typography 應該在 Type.kt 中有定義
        content = content
    )
}