package com.example.mdgapp.ui.component

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Download
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp

@Composable
fun DownloadReportButton(modifier: Modifier = Modifier) {
    val context = LocalContext.current
    Button(
        onClick = {
            // TODO: 實作 PDF 下載邏輯
            Toast.makeText(context, "開始下載報表...", Toast.LENGTH_SHORT).show()
        },
        modifier = modifier
            .fillMaxWidth()
            .height(50.dp),
        colors = ButtonDefaults.buttonColors(containerColor = Color.White)
    ) {
        Icon(
            imageVector = Icons.Default.Download,
            contentDescription = "下載圖示",
            tint = Color.Black
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text("下載 PDF 報表", color = Color.Black)
    }
}
    