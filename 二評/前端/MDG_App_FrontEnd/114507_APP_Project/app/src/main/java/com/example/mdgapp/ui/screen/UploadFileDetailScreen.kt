package com.example.mdgapp.ui.screen

import android.provider.OpenableColumns
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.mdgapp.data.model.UploadedFile
import androidx.compose.ui.Alignment

@Composable
fun UploadFileDetailScreen(
    fileId: String?,
    navController: NavController? = null
) {
    val context = LocalContext.current
    val isNew = fileId == "new" || fileId == null

    // 假資料：實際可從 ViewModel 根據 fileId 查詢
    val dummyFile = UploadedFile(
        id = fileId ?: "new",
        title = "吾駕仙操作手冊",
        description = "包含內輪差與疲勞警示設定說明。",
        publishDate = "2025/08/05",
        expireDate = "2025/09/01",
        uploader = "技術支援部"
    )

    var selectedFileName by remember { mutableStateOf("") }

    // 選擇檔案
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            val cursor = context.contentResolver.query(uri, null, null, null, null)
            cursor?.use {
                val nameIndex = it.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (it.moveToFirst() && nameIndex != -1) {
                    selectedFileName = it.getString(nameIndex)
                }
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(24.dp)
    ) {
        Text(
            if (isNew) "新增上傳檔案" else "檔案詳情",
            fontSize = 24.sp,
            color = Color.White
        )
        Spacer(modifier = Modifier.height(20.dp))

        Text("標題：${dummyFile.title}", color = Color.White, fontSize = 18.sp)
        Text("說明：${dummyFile.description}", color = Color.LightGray, fontSize = 16.sp)
        Text("發佈日：${dummyFile.publishDate}", color = Color.Gray, fontSize = 14.sp)
        Text("截止日：${dummyFile.expireDate}", color = Color.Gray, fontSize = 14.sp)
        Text("發佈者：${dummyFile.uploader}", color = Color.Gray, fontSize = 14.sp)

        Spacer(modifier = Modifier.height(24.dp))

        // 顯示選擇的檔案名稱
        if (selectedFileName.isNotEmpty()) {
            Text("已選擇檔案：$selectedFileName", color = Color.White)
            Spacer(modifier = Modifier.height(12.dp))
        }

        // 選擇檔案按鈕
        Button(
            onClick = { filePickerLauncher.launch("*/*") },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color.White),
            shape = RoundedCornerShape(16.dp)
        ) {
            Text("選擇檔案", color = Color.Black)
        }

        Spacer(modifier = Modifier.height(24.dp))

        // 確認上傳／重新上傳按鈕
        Button(
            onClick = {
                // ⏳ 模擬上傳動作，實作請串接 API
                navController?.popBackStack()
            },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color.White),
            shape = RoundedCornerShape(16.dp),
            enabled = selectedFileName.isNotEmpty() // 若未選檔案則禁用
        ) {
            Text(
                if (isNew) "確定上傳" else "確認重新上傳",
                color = Color.Black
            )
        }
    }
}
