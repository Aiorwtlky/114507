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
        composable("login") { LoginScreen(navController = navController) } // 功能：登入
        composable("register") { RegisterScreen(navController = navController) } // 功能：註冊
        composable("launch") { LaunchScreen(navController = navController) } // 功能：啟動畫面
        composable("home") {
            UnifiedHomeScreen(navController = navController, userRole = "driver")
        } // 功能：駕駛員首頁
        composable("managerHome") {
            UnifiedHomeScreen(navController = navController, userRole = "manager")
        } // 功能：管理者首頁
        composable("profile") { ProfileScreen(navController = navController) } // 功能：駕駛員個人資料
        composable("managerProfile") { ManagerProfileScreen(navController = navController) } // 功能：管理者個人資料

        // ==================== 功能性頁面路由 ====================
        composable("qrScan") { QrScanScreen(navController = navController) } // 功能：QR Code 掃描

        /*composable("routeTracking") {
            RouteTrackingScreen(
                navController = navController
            )
        }*/ // 功能：行車路線追蹤（目前停用）

        // ==================== 駕駛員專用路由 ====================
        composable("announcementList") { AnnouncementListScreen(navController = navController) } // 功能：公告列表
        composable(
            "announcementDetail/{title}",
            arguments = listOf(navArgument("title") { type = NavType.StringType })
        ) { backStackEntry ->
            AnnouncementDetailScreen(
                title = backStackEntry.arguments?.getString("title") ?: "無標題",
                navController = navController
            )
        } // 功能：公告詳情

        // --- 駕駛員報表 ---
        composable("reportList") {
            ReportListScreen(navController = navController, viewModel = reportViewModel)
        } // 功能：報表列表
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
        } // 功能：報表詳情

        // --- 駕駛員下載 ---
        composable("downloadFileList") {
            DownloadFileListScreen(
                navController = navController,
                viewModel = driverDownloadViewModel
            )
        } // 功能：檔案下載列表
        composable(
            "videoList/{date}",
            arguments = listOf(navArgument("date") { type = NavType.StringType })
        ) { backStackEntry ->
            VideoListScreen(
                navController = navController,
                dateString = backStackEntry.arguments?.getString("date"),
                viewModel = driverDownloadViewModel
            )
        } // 功能：行車影片列表（依日期）

        // --- 駕駛員歷史與群組 ---
        composable("driverHistory") { DriverHistoryScreen(navController = navController) } // 功能：駕駛歷史紀錄
        composable("driverGroupScreen") {
            GroupManagementScreen(
                navController = navController,
                viewModel = groupManagementViewModel,
                isManager = false
            )
        } // 功能：駕駛員群組管理


        // ==================== 管理者專用路由 ====================
        composable("managerAnnouncementList") {
            ManagerAnnouncementListScreen(navController = navController, viewModel = managerAnnouncementViewModel)
        } // 功能：管理者公告列表
        composable("managerAddAnnouncement") {
            ManagerAddAnnouncementScreen(navController = navController, viewModel = managerAnnouncementViewModel)
        } // 功能：新增公告
        composable(
            "managerEditAnnouncement/{announcementId}",
            arguments = listOf(navArgument("announcementId") { type = NavType.IntType })
        ) { backStackEntry ->
            ManagerAddAnnouncementScreen(
                navController = navController,
                announcementId = backStackEntry.arguments?.getInt("announcementId"),
                viewModel = managerAnnouncementViewModel
            )
        } // 功能：編輯公告

        composable("managerSelfDownloadList") {
            DownloadFileListScreen(navController = navController, viewModel = driverDownloadViewModel)
        } // 功能：管理者自身檔案下載
        composable("managerSelfReportList") {
            ReportListScreen(navController = navController, viewModel = reportViewModel)
        } // 功能：管理者自身報表

        composable("groupManagement") {
            GroupManagementScreen(
                navController = navController,
                viewModel = groupManagementViewModel,
                isManager = true
            )
        } // 功能：管理群組
        composable("groupSettings") {
            GroupSettingsScreen(navController = navController, viewModel = groupManagementViewModel)
        } // 功能：群組設定
        composable("addMember") {
            AddMemberScreen(navController = navController, viewModel = groupManagementViewModel)
        } // 功能：新增成員
        composable(
            "memberDetail/{memberId}",
            arguments = listOf(navArgument("memberId") { type = NavType.StringType })
        ) { backStackEntry ->
            MemberDetailScreen(
                navController = navController,
                memberId = backStackEntry.arguments?.getString("memberId"),
                viewModel = groupManagementViewModel
            )
        } // 功能：成員詳情

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
        } // 功能：某駕駛的報表日期列表
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
        } // 功能：管理者查看報表詳情

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
        } // 功能：管理者下載檔案列表（依駕駛）
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
        } // 功能：管理者查看影片列表（依駕駛與日期）

        composable("managerHistory") {
            ManagerHistoryScreen(navController = navController)
        } // 功能：管理者歷史紀錄
    }
}
