package com.example.mdgapp.navigation

import androidx.compose.runtime.*
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.example.mdgapp.data.viewmodel.*
import com.example.mdgapp.ui.screen.*

@Composable
fun AppNavGraph(navController: NavHostController) {
    // 只保留駕駛員需要的共享 ViewModel
    val reportViewModel: ReportViewModel = viewModel()
    val groupManagementViewModel: GroupManagementViewModel = viewModel()
    val driverDownloadViewModel: DriverDownloadViewModel = viewModel()


    NavHost(navController = navController, startDestination = "launch") {

        // ==================== 基礎流程路由 ====================
        composable("login") { LoginScreen(navController = navController) }
        composable("register") { RegisterScreen(navController = navController) }
        composable("launch") { LaunchScreen(navController = navController) }
        composable("home") {
            // ✅ 將 reportViewModel 傳遞給 UnifiedHomeScreen
            UnifiedHomeScreen(
                navController = navController,
                reportViewModel = reportViewModel
            )
        }
        composable("profile") { ProfileScreen(navController = navController) }

        // ==================== 功能性頁面路由 ====================
        // ✅ 2. 新增打卡功能的完整流程
        composable("checkIn") {
            CheckInOptionScreen(navController = navController)
        }
        composable("nfcCheckIn") {
            NfcCheckInScreen(navController = navController)
        }
        composable("cardCheckIn") {
            CardCheckInScreen(navController = navController)
        }

        // ==================== 駕駛員專用路由 ====================
        composable("announcementList") { AnnouncementListScreen(navController = navController) }
        composable(
            "announcementDetail/{title}",
            arguments = listOf(navArgument("title") { type = NavType.StringType })
        ) { backStackEntry ->
            AnnouncementDetailScreen(
                title = backStackEntry.arguments?.getString("title") ?: "無標題",
                navController = navController
            )
        }

        // --- 駕駛員報表 ---
        composable("reportList") {
            ReportListScreen(navController = navController, viewModel = reportViewModel)
        }
        // ✅ 修正 #1：修正 ReportDetailScreen 的呼叫方式
        composable(
            route = "reportDetail/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            ReportDetailScreen(
                navController = navController,
                dateString = backStackEntry.arguments?.getString("date"),
                viewModel = reportViewModel
            )
        }

        // --- 駕駛員下載 ---
        composable("downloadFileList") {
            DownloadFileListScreen(navController = navController, viewModel = driverDownloadViewModel)
        }
        composable(
            "videoList/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            VideoListScreen(
                navController = navController,
                dateString = backStackEntry.arguments?.getString("date"),
                viewModel = driverDownloadViewModel
            )
        }

        // --- 駕駛員歷史與群組 ---
        composable("driverHistory") { DriverHistoryScreen(navController = navController) }

        // ✅ 修正 #2：移除 GroupManagementScreen 的 isManager 參數
        composable("driverGroupScreen") {
            GroupManagementScreen(
                navController = navController,
                viewModel = groupManagementViewModel
            )
        }
    }
}