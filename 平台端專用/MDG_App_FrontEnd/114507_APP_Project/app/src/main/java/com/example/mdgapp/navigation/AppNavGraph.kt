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

    // ✅ 新增 RouteTrackingViewModel 的宣告，以確保其生命週期與 NavHost 綁定
    val routeTrackingViewModel: RouteTrackingViewModel = viewModel()

    NavHost(navController = navController, startDestination = "launch") {

        // ==================== 基礎流程路由 ====================
        composable("login") { LoginScreen(navController = navController) }
        // ✅ 註解掉註冊頁面路由（保留以備後用）
        // composable("register") { RegisterScreen(navController = navController) }
        composable("launch") { LaunchScreen(navController = navController) }

        // ✅ 主頁面 - 使用新的簡化版首頁
        composable("home") {
            UnifiedHomeScreen(navController = navController)
        }

        // 個人資料頁面
        composable("profile") { ProfileScreen(navController = navController) }

        // ==================== 打卡功能路由 ====================
        // 打卡選項頁面
        composable("NfcLogIn") {
            NfcLogInScreen(navController = navController)
        }
        // 手機 NFC 註冊
        composable("nfcCheckIn") {
            NfcCheckInScreen(navController = navController)
        }
        // 實體卡片註冊
        composable("cardCheckIn") {
            CardCheckInScreen(navController = navController)
        }

        // ==================== 行駛軌跡功能路由 (第二階段實作) ====================
        // ✅ 新增行駛軌跡頁面路由
        composable("route_tracking_screen") {
            // 將 RouteTrackingViewModel 傳遞給畫面，以便控制追蹤狀態
            RouteTrackingScreen(
                navController = navController,
                viewModel = routeTrackingViewModel
            )
        }

        // ==================== 以下路由暫時註解（保留以備後用）====================

        // --- 公告相關 ---
        // composable("announcementList") { AnnouncementListScreen(navController = navController) }
        // composable(
        //     "announcementDetail/{title}",
        //     arguments = listOf(navArgument("title") { type = NavType.StringType })
        // ) { backStackEntry ->
        //     AnnouncementDetailScreen(
        //         title = backStackEntry.arguments?.getString("title") ?: "無標題",
        //         navController = navController
        //     )
        // }

        // --- 駕駛員報表 ---
        // composable("reportList") {
        //     ReportListScreen(navController = navController, viewModel = reportViewModel)
        // }
        // composable(
        //     route = "reportDetail/{date}",
        //     arguments = listOf(navArgument("date") { type = NavType.StringType })
        // ) { backStackEntry ->
        //     ReportDetailScreen(
        //         navController = navController,
        //         dateString = backStackEntry.arguments?.getString("date"),
        //         viewModel = reportViewModel
        //     )
        // }

        // --- 駕駛員下載 ---
        // composable("downloadFileList") {
        //     DownloadFileListScreen(navController = navController, viewModel = driverDownloadViewModel)
        // }
        // composable(
        //     "videoList/{date}",
        //     arguments = listOf(navArgument("date") { type = NavType.StringType })
        // ) { backStackEntry ->
        //     VideoListScreen(
        //         navController = navController,
        //         dateString = backStackEntry.arguments?.getString("date"),
        //         viewModel = driverDownloadViewModel
        //     )
        // }

        // --- 駕駛員歷史與群組 ---
        // composable("driverHistory") { DriverHistoryScreen(navController = navController) }
        // composable("driverGroupScreen") {
        //     GroupManagementScreen(
        //         navController = navController,
        //         viewModel = groupManagementViewModel
        //     )
        // }
    }
}