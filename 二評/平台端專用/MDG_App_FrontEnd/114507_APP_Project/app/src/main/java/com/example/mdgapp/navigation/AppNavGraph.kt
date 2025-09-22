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
    // 建立所有需要的共享 ViewModel
    val reportViewModel: ReportViewModel = viewModel()
    val managerReportViewModel: ManagerReportViewModel = viewModel()
    val managerAnnouncementViewModel: ManagerAnnouncementViewModel = viewModel()
    val groupManagementViewModel: GroupManagementViewModel = viewModel()
    val driverDownloadViewModel: DriverDownloadViewModel = viewModel()
    val managerDownloadViewModel: ManagerDownloadViewModel = viewModel()

    NavHost(navController = navController, startDestination = "launch") {

        // ==================== 基礎流程路由 ====================
        composable("register") { RegisterScreen(navController = navController) }
        composable("launch") { LaunchScreen(navController = navController) }
        // ✅ 將 home 路由指向 UnifiedHomeScreen，並傳入 "driver" 角色
        composable("home") {
            UnifiedHomeScreen(navController = navController, userRole = "driver")
        }
// ✅ 將 managerHome 路由指向 UnifiedHomeScreen，並傳入 "manager" 角色
        composable("managerHome") {
            UnifiedHomeScreen(navController = navController, userRole = "manager")
        }
        composable("profile") { ProfileScreen(navController = navController) }
        composable("managerProfile") { ManagerProfileScreen(navController = navController) }

        // ==================== 功能性頁面路由 ====================
        composable("qrScan") { QrScanScreen(navController = navController) }
        composable("routeTracking") {
            val viewModel: RouteTrackingViewModel = viewModel()
            val uiState by viewModel.uiState.collectAsState()
            RouteTrackingScreen(
                navController = navController,
                totalDistance = uiState.totalDistance,
                time = uiState.time
            )
        }

        // ==================== 駕駛員專用路由 ====================
        composable("announcementList") { AnnouncementListScreen(navController = navController) }
        composable("reportList") {
            ReportListScreen(navController = navController, viewModel = reportViewModel)
        }
        composable("driverHistory") {
            DriverHistoryScreen(navController = navController)
        }
        // --- 駕駛員下載流程 ---
        composable("downloadFileList") {
            DownloadFileListScreen(navController = navController, viewModel = driverDownloadViewModel)
        }
        composable(
            route = "videoList/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            VideoListScreen(
                navController = navController,
                dateString = backStackEntry.arguments?.getString("date"),
                viewModel = driverDownloadViewModel
            )
        }

        // ==================== 管理者專用路由 ====================
        composable("managerAnnouncementList") {
            ManagerAnnouncementListScreen(navController = navController, viewModel = managerAnnouncementViewModel)
        }
        composable("managerAddAnnouncement") {
            ManagerAddAnnouncementScreen(navController = navController, viewModel = managerAnnouncementViewModel)
        }
        // --- 管理者下載流程 ---
        composable("managerDriverSelectionForDownload") {
            ManagerDriverSelectionScreen(navController = navController, viewModel = managerDownloadViewModel)
        }
        composable(
            route = "managerDownloadFileList/{driverId}",
            arguments = listOf(navArgument("driverId") { type = NavType.StringType })
        ) { backStackEntry ->
            ManagerDownloadFileListScreen(
                navController = navController,
                driverId = backStackEntry.arguments?.getString("driverId"),
                viewModel = managerDownloadViewModel
            )
        }
        composable(
            route = "managerVideoList/{driverId}/{date}",
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
        // --- 其他管理者路由 ---
        composable("managerReportDriverList") {
            ManagerReportDriverListScreen(navController = navController, viewModel = managerReportViewModel)
        }
        composable(
            route = "managerReportDateList/{driverId}",
            arguments = listOf(navArgument("driverId") { type = NavType.StringType })
        ) { backStackEntry ->
            ManagerReportDateListScreen(
                navController = navController,
                driverId = backStackEntry.arguments?.getString("driverId"),
                viewModel = managerReportViewModel
            )
        }
        composable("managerReportDetail/{date}") { /* ... */ }
        composable("managerHistory") {
            ManagerHistoryScreen(navController = navController)
        }
        composable("groupManagement") {
            GroupManagementScreen(navController = navController, viewModel = groupManagementViewModel)
        }
        composable("groupSettings") {
            GroupSettingsScreen(navController = navController, viewModel = groupManagementViewModel)
        }
        composable("addMember") {
            AddMemberScreen(navController = navController, viewModel = groupManagementViewModel)
        }
        composable(
            route = "memberDetail/{memberId}",
            arguments = listOf(navArgument("memberId") { type = NavType.StringType })
        ) { backStackEntry ->
            MemberDetailScreen(
                navController = navController,
                memberId = backStackEntry.arguments?.getString("memberId"),
                viewModel = groupManagementViewModel
            )
        }
    }
}