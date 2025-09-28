package com.example.mdgapp.navigation

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
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
    // 建立所有需要的共享 ViewModel
    val reportViewModel: ReportViewModel = viewModel()
    val managerReportViewModel: ManagerReportViewModel = viewModel()
    val managerAnnouncementViewModel: ManagerAnnouncementViewModel = viewModel()
    val groupManagementViewModel: GroupManagementViewModel = viewModel()
    val driverDownloadViewModel: DriverDownloadViewModel = viewModel()
    val managerDownloadViewModel: ManagerDownloadViewModel = viewModel()

    NavHost(
        navController = navController,
        startDestination = "launch",
        modifier = Modifier.fillMaxSize() // ✅ 修正一：為 NavHost 設定大小
    ) {

        // ==================== 基礎流程路由 ====================
        composable("register") { RegisterScreen(navController = navController) }
        composable("launch") { LaunchScreen(navController = navController) }
        composable("home") {
            UnifiedHomeScreen(navController = navController, userRole = "driver")
        }
        composable("managerHome") {
            UnifiedHomeScreen(navController = navController, userRole = "manager")
        }
        composable("profile") { ProfileScreen(navController = navController) }
        composable("managerProfile") { ManagerProfileScreen(navController = navController) }

        // ==================== 功能性頁面路由 ====================
        composable("qrScan") { QrScanScreen(navController = navController) }

        // ✅ 修正二：移除錯誤的巢狀結構，直接呼叫 Screen
        composable("routeTracking") {
            RouteTrackingScreen(
                navController = navController
            )
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
        composable(
            "reportDetail/{date}",
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
            DownloadFileListScreen(
                navController = navController,
                viewModel = driverDownloadViewModel
            )
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

        composable("driverGroupScreen") {
            GroupManagementScreen(
                navController = navController,
                viewModel = groupManagementViewModel,
                isManager = false
            )
        }


        // ==================== 管理者專用路由 ====================
        composable("managerAnnouncementList") {
            ManagerAnnouncementListScreen(navController = navController, viewModel = managerAnnouncementViewModel)
        }
        composable("managerAddAnnouncement") {
            ManagerAddAnnouncementScreen(navController = navController, viewModel = managerAnnouncementViewModel)
        }
        composable(
            "managerEditAnnouncement/{announcementId}",
            arguments = listOf(navArgument("announcementId") { type = NavType.IntType })
        ) { backStackEntry ->
            ManagerAddAnnouncementScreen(
                navController = navController,
                announcementId = backStackEntry.arguments?.getInt("announcementId"),
                viewModel = managerAnnouncementViewModel
            )
        }

        composable("managerSelfDownloadList") {
            DownloadFileListScreen(navController = navController, viewModel = driverDownloadViewModel)
        }
        composable("managerSelfReportList") {
            ReportListScreen(navController = navController, viewModel = reportViewModel)
        }

        composable("groupManagement") {
            GroupManagementScreen(
                navController = navController,
                viewModel = groupManagementViewModel,
                isManager = true
            )
        }
        composable("groupSettings") {
            GroupSettingsScreen(navController = navController, viewModel = groupManagementViewModel)
        }
        composable("addMember") {
            AddMemberScreen(navController = navController, viewModel = groupManagementViewModel)
        }
        composable(
            "memberDetail/{memberId}",
            arguments = listOf(navArgument("memberId") { type = NavType.StringType })
        ) { backStackEntry ->
            MemberDetailScreen(
                navController = navController,
                memberId = backStackEntry.arguments?.getString("memberId"),
                viewModel = groupManagementViewModel
            )
        }

        composable(
            "managerReportDateList/{driverId}",
            arguments = listOf(navArgument("driverId") { type = NavType.StringType })
        ) { backStackEntry ->
            ManagerReportDateListScreen(
                navController = navController,
                driverId = backStackEntry.arguments?.getString("driverId"),
                viewModel = managerReportViewModel
            )
        }
        composable(
            "managerReportDetail/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            ManagerReportDetailScreen(
                navController = navController,
                dateString = backStackEntry.arguments?.getString("date"),
                viewModel = managerReportViewModel
            )
        }
        composable(
            "managerDownloadFileList/{driverId}",
            arguments = listOf(navArgument("driverId") { type = NavType.StringType })
        ) { backStackEntry ->
            ManagerDownloadFileListScreen(
                navController = navController,
                driverId = backStackEntry.arguments?.getString("driverId"),
                viewModel = managerDownloadViewModel
            )
        }
        composable(
            "managerVideoList/{driverId}/{date}",
            arguments = listOf(
                navArgument("driverId") { type = NavType.StringType },
                navArgument("date") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            ManagerVideoListScreen(
                navController = navController,
                dateString = backStackEntry.arguments?.getString("date"),
                viewModel = managerDownloadViewModel
            )
        }

        composable("managerHistory") {
            ManagerHistoryScreen(navController = navController)
        }
    }
}