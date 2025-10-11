// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/component/InfoCard.kt

package com.example.mdgapp.ui.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.draw.clip
import com.example.mdgapp.ui.theme.iOsBlue
import com.example.mdgapp.ui.theme.iOsComponentBackground
import com.example.mdgapp.ui.theme.iOsTextPrimary
import com.example.mdgapp.ui.theme.iOsTextSecondary

@Composable
fun InfoCard(
    value: Int,
    label: String,
    fillColor: Color,
    backgroundColor: Color,
    modifier: Modifier = Modifier
) {
    val progress = (value.coerceIn(0, 100)) / 100f

    Card(
        modifier = modifier.height(100.dp),
        // ✅ 背景色改為主題的白色
        colors = CardDefaults.cardColors(containerColor = iOsComponentBackground),
        elevation = CardDefaults.cardElevation(4.dp),
        shape = RoundedCornerShape(12.dp),
        // ✅ 新增藍色邊框
        border = BorderStroke(1.dp, iOsBlue)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text("$value", color = iOsTextPrimary, fontSize = 20.sp)
            Text(label, color = iOsTextSecondary, fontSize = 12.sp)
            LinearProgressIndicator(
                progress = progress,
                color = fillColor,
                trackColor = backgroundColor,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .clip(RoundedCornerShape(4.dp))
            )
        }
    }
}