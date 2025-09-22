package com.example.mdgapp.ui.component

import androidx.compose.foundation.layout.size
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.mdgapp.R

@Composable
fun AppBottomBar(navController: NavController, userRole: String) {
    NavigationBar(
        // 您可以依照需求調整高度和顏色
        // modifier = Modifier.height(75.dp),
        containerColor = Color.Black
    ) {
        val labelFontSize = 12.sp
        val iconSize = 24.dp
        val itemColors = NavigationBarItemDefaults.colors(
            indicatorColor = Color.Transparent,
            unselectedIconColor = Color.White,
            unselectedTextColor = Color.White
        )

        // 項目 1: 行駛軌跡 (對所有角色顯示)
        NavigationBarItem(
            selected = false,
            onClick = { navController.navigate("routeTracking") },
            icon = { Icon(painterResource(id = R.drawable.ic_map), "行駛軌跡", modifier = Modifier.size(iconSize)) },
            label = { Text("行駛軌跡", fontSize = labelFontSize) },
            colors = itemColors
        )

        // 項目 2: 群組
        NavigationBarItem(
            selected = false,
            onClick = {
                val route = if (userRole == "manager") "groupManagement" else "driverGroupScreen"
                navController.navigate(route)
            },
            icon = { Icon(painterResource(id = R.drawable.ic_group), "群組", modifier = Modifier.size(iconSize)) },
            label = { Text("群組", fontSize = labelFontSize) },
            colors = itemColors
        )

        // 項目 3: 打卡 (對所有角色顯示)
        NavigationBarItem(
            selected = false,
            onClick = { navController.navigate("qrScan") },
            icon = { Icon(painterResource(id = R.drawable.ic_qr), "打卡", modifier = Modifier.size(iconSize)) },
            label = { Text("打卡", fontSize = labelFontSize) },
            colors = itemColors
        )

        // 項目 4: 報表
        NavigationBarItem(
            selected = false,
            onClick = {
                val route = if (userRole == "manager") "managerReportDriverList" else "reportList"
                navController.navigate(route)
            },
            icon = { Icon(painterResource(id = R.drawable.ic_post), "報表", modifier = Modifier.size(iconSize)) },
            label = { Text("報表", fontSize = labelFontSize) },
            colors = itemColors
        )

        // 項目 5: 我的
        NavigationBarItem(
            selected = false,
            onClick = {
                val route = if (userRole == "manager") "managerProfile" else "profile"
                navController.navigate(route)
            },
            icon = { Icon(painterResource(id = R.drawable.ic_person), "我的", modifier = Modifier.size(iconSize)) },
            label = { Text("我的", fontSize = labelFontSize) },
            colors = itemColors
        )
    }
}