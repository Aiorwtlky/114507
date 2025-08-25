package com.example.mdgapp.ui.component

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.DrawerState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.mdgapp.R
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

@Composable
fun TopMenuBar(
    coroutineScope: CoroutineScope,
    drawerState: DrawerState,
    selectedMenu: String,
    onMenuSelected: (String) -> Unit,
    modifier: Modifier = Modifier,
    navController: NavController
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(Color.Black.copy(alpha = 0.68f))
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // 👤 頭像按鈕
        Image(
            painter = painterResource(id = R.drawable.jiboda1),
            contentDescription = "User Avatar",
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
                .background(Color.Gray)
                .clickable {
                    coroutineScope.launch {
                        if (drawerState.isClosed) drawerState.open()
                        else drawerState.close()
                    }
                }
        )

        // 🔘 三個選單按鈕
        listOf("首頁", "公告", "下載").forEach { label ->
            Surface(
                shape = RoundedCornerShape(20.dp),
                color = if (selectedMenu == label) Color.White else Color.Gray,
                modifier = Modifier
                    .height(32.dp)
                    .clickable { onMenuSelected(label) }
            ) {
                // 為了讓文字在按鈕中垂直置中，我們用 Box 包起來
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.padding(horizontal = 12.dp)
                ) {
                    Text(
                        text = label,
                        color = if (selectedMenu == label) Color.Black else Color.White,
                        fontSize = 14.sp
                    )
                }
            }
        }
    }
}
