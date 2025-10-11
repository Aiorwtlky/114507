// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/component/ProfileComponents.kt

package com.example.mdgapp.ui.component

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.mdgapp.data.model.LinkedAccount
import com.example.mdgapp.ui.theme.*

@Composable
fun ProfileHeader(name: String, employeeId: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 24.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(80.dp)
                .clip(CircleShape)
                .background(iOsComponentBackground), // ✅ 背景改為主題白色
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = "個人頭像",
                tint = iOsTextSecondary, // ✅ 圖示改為主題灰色
                modifier = Modifier.size(48.dp)
            )
        }
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(name, fontSize = 22.sp, fontWeight = FontWeight.Bold, color = iOsTextPrimary)
            Text("員工編號: $employeeId", fontSize = 14.sp, color = iOsTextSecondary)
        }
    }
}

@Composable
fun ProfileSection(title: String, content: @Composable ColumnScope.() -> Unit) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = title,
            color = iOsTextSecondary, // ✅ 文字改為主題灰色
            fontSize = 14.sp,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        Card(
            colors = CardDefaults.cardColors(containerColor = iOsComponentBackground), // ✅ 背景改為主題白色
            modifier = Modifier.fillMaxWidth(),
            border = BorderStroke(1.dp, iOsBlue) // ✅ 新增藍色邊框
        ) {
            Column(content = content)
        }
    }
}

@Composable
fun HistorySection(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = title,
            color = iOsTextPrimary, // ✅ 文字改為主題黑色
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        Card(
            colors = CardDefaults.cardColors(containerColor = iOsComponentBackground), // ✅ 背景改為主題白色
            modifier = Modifier.fillMaxWidth(),
            border = BorderStroke(1.dp, iOsBlue) // ✅ 新增藍色邊框
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                content = content
            )
        }
    }
}

@Composable
fun InfoRow(label: String, value: String, isClickable: Boolean = false, onClick: () -> Unit = {}) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = isClickable, onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, color = iOsTextPrimary) // ✅ 文字改為主題黑色
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(value, color = iOsTextSecondary) // ✅ 文字改為主題灰色
            if (isClickable) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                    contentDescription = null,
                    tint = iOsTextSecondary, // ✅ 圖示改為主題灰色
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}

@Composable
fun SettingsSwitchRow(label: String, isChecked: Boolean, onCheckedChange: (Boolean) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, color = iOsTextPrimary) // ✅ 文字改為主題黑色
        Switch(
            checked = isChecked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = Color.White,
                checkedTrackColor = iOsBlue, // ✅ Switch 開啟顏色改為藍色
                uncheckedThumbColor = Color.White,
                uncheckedTrackColor = Color.Gray
            )
        )
    }
}

@Composable
fun LinkedAccountRow(account: LinkedAccount) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            painter = painterResource(id = account.iconResId),
            contentDescription = account.platform,
            modifier = Modifier.size(24.dp),
            tint = Color.Unspecified
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(account.platform, color = iOsTextPrimary) // ✅ 文字改為主題黑色
            Text(account.username, color = iOsTextSecondary, fontSize = 12.sp) // ✅ 文字改為主題灰色
        }
        TextButton(onClick = { /* TODO: 處理取消連結 */ }) {
            Text("取消連結", color = Color.Red)
        }
    }
}