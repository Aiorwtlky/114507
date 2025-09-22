package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ManagerDownloadViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerDriverSelectionScreen(
    navController: NavController,
    viewModel: ManagerDownloadViewModel = viewModel()
) {
    val drivers by viewModel.drivers.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("選擇駕駛員") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Black,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        },
        containerColor = Color.Black
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier.padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(drivers, key = { it.driverId }) { driver ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    onClick = {
                        // 導航到該駕駛的檔案列表，並傳遞 driverId
                        navController.navigate("downloadFileList/${driver.driverId}")
                    },
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E))
                ) {
                    ListItem(
                        headlineContent = { Text(driver.driverName, color = Color.White) },
                        supportingContent = { Text("駕駛編號: ${driver.driverId}", color = Color.Gray) }
                    )
                }
            }
        }
    }
}