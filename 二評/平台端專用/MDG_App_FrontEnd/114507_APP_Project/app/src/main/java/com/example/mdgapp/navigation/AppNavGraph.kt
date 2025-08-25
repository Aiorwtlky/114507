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
import com.example.mdgapp.data.viewmodel.ReportViewModel
import com.example.mdgapp.data.viewmodel.RouteTrackingViewModel
import com.example.mdgapp.ui.screen.*

@Composable
fun AppNavGraph(navController: NavHostController) {
    // ✅ 修正點 1：將 ViewModel 的建立移到 NavHost 外層
    // 這樣 viewModel 的生命週期會與 AppNavGraph 綁定
    val reportViewModel: ReportViewModel = viewModel()

    NavHost(navController = navController, startDestination = "register") {

        // ... 其他路由 ...
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
        composable("downloadFileList") { DownloadFileListScreen(navController = navController) }
        composable(
            route = "videoList/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            VideoListScreen(navController = navController, dateString = backStackEntry.arguments?.getString("date"))
        }
        // ...

        // ==================== 駕駛報表流程路由 ====================

        composable("reportList") {
            // 將共享的實例傳遞給列表畫面
            ReportListScreen(navController = navController, viewModel = reportViewModel)
        }
        composable(
            route = "reportDetail/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            // 將同一個共享的實例傳遞給詳情畫面
            ReportDetailScreen(
                navController = navController,
                dateString = backStackEntry.arguments?.getString("date"),
                viewModel = reportViewModel
            )
        }
        // =========================================================
        // 在 AppNavGraph.kt 中
        composable("profile") {
            ProfileScreen(navController = navController)
        }
    }
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    val navController = rememberNavController()
    AppNavGraph(navController = navController)
}
