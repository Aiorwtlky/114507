package com.example.mdgapp.navigation

import androidx.compose.runtime.*
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.example.mdgapp.data.viewmodel.RouteTrackingViewModel
import com.example.mdgapp.model.ChatItem
import com.example.mdgapp.ui.screen.*

val chatList = listOf(
    ChatItem(id = 1, name = "季博達"),
    ChatItem(id = 2, name = "純愛戰神"),
    ChatItem(id = 3, name = "haerin")
)

@Composable
fun AppNavGraph(navController: NavHostController) {
    NavHost(navController = navController, startDestination = "launch") {

        composable("launch") {
            LaunchScreen(navController)
        }

        composable("register") {
            RegisterScreen(navController)
        }

        composable("home") {
            HomeScreen(navController)
        }

        composable("qrScan") {
            QrScanScreen(navController)
        }

        composable("routeTracking") {
            val viewModel: RouteTrackingViewModel = viewModel()
            val uiState by viewModel.uiState.collectAsState()

            RouteTrackingScreen(
                totalDistance = uiState.totalDistance,
                time = uiState.time
            )
        }

        // 公告列表
        composable("announcementList") {
            AnnouncementListScreen(navController)
        }

        // 上傳清單
        composable("uploadFileList") {
            UploadFileListScreen(navController)
        }


        composable("announcementDetail/{title}") { backStackEntry ->
            val title = backStackEntry.arguments?.getString("title") ?: "公告"
            AnnouncementDetailScreen(title = title, navController = navController)
        }


        composable("uploadFileDetail/{fileId}") { backStackEntry ->
            val fileId = backStackEntry.arguments?.getString("fileId")
            UploadFileDetailScreen(fileId = fileId, navController = navController)
        }


    }
}
