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
import com.example.mdgapp.ui.screen.*

@Composable
fun AppNavGraph(navController: NavHostController) {
    // 建立可供駕駛員報表流程共享的 ViewModel
    val reportViewModel: ReportViewModel = viewModel()
    // 建立可供管理者報表流程共享的 ViewModel
    val managerReportViewModel: ManagerReportViewModel = viewModel()

    NavHost(navController = navController, startDestination = "register") {

        // ==================== 基礎流程路由 ====================
        composable("register") { RegisterScreen(navController) }
        composable("home") { HomeScreen(navController) }
        composable("managerHome") { ManagerHomeScreen(navController) }
        composable("profile") { ProfileScreen(navController = navController) }
        // ... 其他基礎路由 ...


        // ==================== 駕駛員報表流程路由 ====================
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

        // ==================== 管理者報表流程路由 ====================
        composable("managerReportDriverList") {
            ManagerReportDriverListScreen(
                navController = navController,
                viewModel = managerReportViewModel
            )
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
    }
}