// 檔案路徑: app/src/main/java/com/example/mdgapp/navigation/AppNavGraph.kt

package com.example.mdgapp.navigation

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
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
        startDestination = "home",
        modifier = Modifier.fillMaxSize()
    ) {

        // ==================== 基礎流程路由 ====================
        composable("login") { LoginScreen(navController = navController) }
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

        /*composable("routeTracking") {
            RouteTrackingScreen(
                navController = navController
            )
        }*/

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
        // ▼▼▼ 【修改重點 1】修正駕駛員報表詳情的呼叫方式 ▼▼▼
        composable(
            "reportDetail/{tripId}",
            arguments = listOf(navArgument("tripId") { type = NavType.IntType })
        ) { backStackEntry ->
            val report by reportViewModel.selectedReport.collectAsStateWithLifecycle()
            ReportDetailScreen(
                navController = navController,
                tripId = backStackEntry.arguments?.getInt("tripId"),
                report = report,
                onFetchDetails = { id -> reportViewModel.fetchTripDetails(id) }
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

        // --- 管理者報表 ---
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

        // ▼▼▼ 【修改重點 2】刪除所有舊的、重複的定義，只保留這一個正確的版本 ▼▼▼
        composable(
            "managerReportDetail/{tripId}",
            arguments = listOf(navArgument("tripId") { type = NavType.IntType })
        ) { backStackEntry ->
            val report by managerReportViewModel.selectedReportDetail.collectAsStateWithLifecycle()
            ReportDetailScreen(
                navController = navController,
                tripId = backStackEntry.arguments?.getInt("tripId"),
                report = report,
                onFetchDetails = { id -> managerReportViewModel.fetchTripDetails(id) }
            )
        }

        // --- 管理者下載 ---
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