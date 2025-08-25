package com.example.mdgapp.navigation

import androidx.compose.runtime.*
import androidx.compose.ui.tooling.preview.Preview
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.mdgapp.data.viewmodel.RouteTrackingViewModel
import com.example.mdgapp.ui.screen.*

@Composable
fun AppNavGraph(navController: NavHostController) {
    NavHost(navController = navController, startDestination = "launch") {

        // ... 其他路由保持不變 ...
        composable("launch") { LaunchScreen(navController) }
        composable("register") { RegisterScreen(navController) }
        composable("home") { HomeScreen(navController) }
        composable("qrScan") { QrScanScreen(navController) }
        composable("routeTracking") {
            val viewModel: RouteTrackingViewModel = viewModel()
            val uiState by viewModel.uiState.collectAsState()
            RouteTrackingScreen(
                totalDistance = uiState.totalDistance,
                time = uiState.time
            )
        }
        composable("announcementList") { AnnouncementListScreen(navController) }
        composable("announcementDetail/{title}") { backStackEntry ->
            val title = backStackEntry.arguments?.getString("title") ?: "公告"
            AnnouncementDetailScreen(title = title, navController = navController)
        }

        // ==================== 影像下載流程路由 ====================

        // 1. 日期列表主畫面 (Master Screen)
        composable("downloadFileList") {
            DownloadFileListScreen(navController = navController)
        }

        // 2. 影片列表詳細畫面 (Detail Screen)
        composable(
            route = "videoList/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            val dateString = backStackEntry.arguments?.getString("date")
            VideoListScreen(navController = navController, dateString = dateString)
        }
        // =========================================================

    }
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    val navController = rememberNavController()
    AppNavGraph(navController = navController)
}
