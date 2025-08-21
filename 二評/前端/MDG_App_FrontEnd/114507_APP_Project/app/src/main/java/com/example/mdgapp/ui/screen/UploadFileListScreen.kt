package com.example.mdgapp.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.* // 👈 這裡包含 remember、mutableStateOf 等
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.mdgapp.data.model.UploadedFile
import androidx.compose.ui.Alignment

@Composable
fun UploadFileListScreen(
    navController: NavController? = null
) {
    // 🔄 Tab 切換狀態：預設是「需上傳」
    var selectedTab by remember { mutableStateOf("需上傳") }

    // 📄 假資料分組
    val pendingFiles = listOf(
        UploadedFile("3", "駕駛異常分析", "請上傳異常數據報表", "2025/08/06", "2025/08/15", "你"),
        UploadedFile("4", "駕駛記錄", "未完成行車紀錄檔案", "2025/08/03", "2025/08/20", "你")
    )
    val uploadedFiles = listOf(
        UploadedFile("1", "安全駕駛守則", "提醒各位駕駛注意盲區與煞車距離。", "2025/08/01", "2025/08/31", "系統管理員"),
        UploadedFile("2", "吾駕仙操作手冊", "包含內輪差與疲勞警示設定說明。", "2025/08/05", "2025/09/01", "技術支援部")
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(16.dp)
    ) {
        // ⬆️ 上方區塊（標題 + 上傳按鈕）
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("上傳管理", fontSize = 24.sp, color = Color.White)
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 🔘 Tab 切換區（需上傳 / 已上傳）
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf("需上傳", "已上傳").forEach { label ->
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = if (selectedTab == label) Color.White else Color.DarkGray,
                    modifier = Modifier
                        .height(32.dp)
                        .clickable { selectedTab = label }
                ) {
                    Text(
                        text = label,
                        color = if (selectedTab == label) Color.Black else Color.LightGray,
                        fontSize = 14.sp,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 📋 清單顯示區
        val listToShow = if (selectedTab == "需上傳") pendingFiles else uploadedFiles

        listToShow.forEach { file ->
            FileCard(file = file, onClick = {
                navController?.navigate("uploadFileDetail/${file.id}")
            })
            Spacer(modifier = Modifier.height(12.dp))
        }
    }
}



@Composable
fun FileCard(file: UploadedFile, onClick: () -> Unit = {}) {
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }, // 加入點擊事件
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(file.title, fontSize = 20.sp, color = Color.White)
            Spacer(modifier = Modifier.height(4.dp))
            Text(file.description, fontSize = 14.sp, color = Color.Gray)
            Spacer(modifier = Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("發佈：${file.publishDate}", fontSize = 12.sp, color = Color.LightGray)
                Text("到期：${file.expireDate}", fontSize = 12.sp, color = Color.LightGray)
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text("發佈者：${file.uploader}", fontSize = 12.sp, color = Color.LightGray)
        }
    }
}