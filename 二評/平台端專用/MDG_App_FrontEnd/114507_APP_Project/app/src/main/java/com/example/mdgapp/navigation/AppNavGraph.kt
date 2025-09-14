package com.example.mdgapp.navigation

import androidx.compose.runtime.*
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.example.mdgapp.data.viewmodel.ManagerReportViewModel
import com.example.mdgapp.data.viewmodel.ReportViewModel
import com.example.mdgapp.data.viewmodel.RouteTrackingViewModel
import com.example.mdgapp.data.viewmodel.ManagerAnnouncementViewModel
import com.example.mdgapp.data.viewmodel.GroupManagementViewModel
import com.example.mdgapp.ui.screen.*

@Composable
fun AppNavGraph(navController: NavHostController) {
    val reportViewModel: ReportViewModel = viewModel()
    val managerReportViewModel: ManagerReportViewModel = viewModel()
    // 1. 在 NavHost 外層建立 ViewModel 實例
    val managerAnnouncementViewModel: ManagerAnnouncementViewModel = viewModel()
    val groupManagementViewModel: GroupManagementViewModel = viewModel()

    NavHost(navController = navController, startDestination = "launch") {

        // ==================== 基礎流程路由 ====================
        composable("register") { RegisterScreen(navController = navController) }
        composable("launch") { LaunchScreen(navController = navController) }
        composable("home") { HomeScreen(navController = navController) }
        composable("managerHome") { ManagerHomeScreen(navController = navController) }
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

        // ==================== 公告與下載流程路由 ====================
        composable("announcementList") { AnnouncementListScreen(navController = navController) }
        composable(
            route = "announcementDetail/{title}",
            arguments = listOf(navArgument("title") { type = NavType.StringType })
        ) { backStackEntry ->
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
        composable("managerAnnouncementList") {
            ManagerAnnouncementListScreen(navController = navController, viewModel = managerAnnouncementViewModel)
        }
        composable("managerAddAnnouncement") {
            ManagerAddAnnouncementScreen(navController = navController, viewModel = managerAnnouncementViewModel)
        }

        // ==================== 駕駛員報表與歷史數據路由 ====================
        composable("reportList") {
            ReportListScreen(navController = navController, viewModel = reportViewModel)
        }
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
        composable("driverHistory") {
            DriverHistoryScreen(navController = navController)
        }

        // ==================== 管理者報表與歷史數據路由 ====================
        composable("managerReportDriverList") {
            ManagerReportDriverListScreen(
                navController = navController,
                viewModel = managerReportViewModel
            )
        }

        // ✅ 新增：管理者選擇駕駛後，顯示其報表日期的路由
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

        // ✅ 新增：管理者選擇日期後，顯示報表詳情的路由
        composable(
            route = "managerReportDetail/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            ManagerReportDetailScreen(
                navController = navController,
                dateString = backStackEntry.arguments?.getString("date"),
                viewModel = managerReportViewModel
            )
        }

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