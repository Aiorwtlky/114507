package com.example.mdgapp.ui.component

import androidx.compose.foundation.layout.RowScope
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.navigation.NavController
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TopMenuBar(
    coroutineScope: CoroutineScope,
    drawerState: DrawerState,
    selectedMenu: String,
    onMenuSelected: (String) -> Unit,
    navController: NavController,
    // ✅ 1. 在函式簽名中加入 actions 參數，並提供一個空的預設值
    actions: @Composable RowScope.() -> Unit = {}
) {
    TopAppBar(
        title = { Text(selectedMenu, color = Color.White) },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = Color.DarkGray,
            titleContentColor = Color.White
        ),
        navigationIcon = {
            IconButton(onClick = {
                coroutineScope.launch {
                    drawerState.open()
                }
            }) {
                Icon(
                    imageVector = Icons.Default.Menu,
                    contentDescription = "開啟側邊選單",
                    tint = Color.White
                )
            }
        },
        // ✅ 2. 將接收到的 actions 參數傳遞給 TopAppBar
        actions = actions
    )
}