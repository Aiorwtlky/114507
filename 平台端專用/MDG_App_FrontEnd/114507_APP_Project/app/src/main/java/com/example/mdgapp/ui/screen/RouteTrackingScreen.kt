// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/RouteTrackingScreen.kt
package com.example.mdgapp.ui.screen

import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.data.viewmodel.RouteTrackingUiState
import com.example.mdgapp.data.viewmodel.RouteTrackingViewModel
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.maps.android.compose.*

@Composable
fun RouteTrackingScreen(
    navController: NavController,
    viewModel: RouteTrackingViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var hasLocationPermission by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        // 只需要精確位置或粗略位置其中之一
        hasLocationPermission = permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true ||
                permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true
    }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(
            arrayOf(
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION
            )
        )
    }

    Scaffold(
        floatingActionButton = {
            RouteTrackingFab(
                isTracking = uiState.isTracking,
                onToggleTracking = {
                    if (uiState.isTracking) {
                        viewModel.stopTracking()
                    } else {
                        viewModel.startTracking()
                    }
                }
            )
        },
        floatingActionButtonPosition = FabPosition.End
    ) { paddingValues ->
        if (hasLocationPermission) {
            RealTimeMapContent(
                uiState = uiState,
                modifier = Modifier.padding(paddingValues),
                onStartTracking = viewModel::startTracking // 傳入開始追蹤函式
            )
        } else {
            Box(
                modifier = Modifier.fillMaxSize().background(Color.Black),
                contentAlignment = Alignment.Center
            ) {
                Text("需要位置權限才能使用此功能", color = Color.White)
            }
        }
    }
}

@Composable
fun RouteTrackingFab(
    isTracking: Boolean,
    onToggleTracking: () -> Unit
) {
    ExtendedFloatingActionButton(
        onClick = onToggleTracking,
        modifier = Modifier.padding(16.dp),
        containerColor = if (isTracking) Color(0xFFEF5350) else Color(0xFF4CAF50), // 紅色停止，綠色開始
        contentColor = Color.White,
        icon = {
            Icon(
                imageVector = if (isTracking) Icons.Filled.Stop else Icons.Filled.PlayArrow,
                contentDescription = if (isTracking) "停止追蹤" else "開始追蹤"
            )
        },
        text = {
            Text(
                text = if (isTracking) "停止追蹤" else "開始追蹤",
                fontWeight = FontWeight.Bold
            )
        }
    )
}


@Composable
private fun RealTimeMapContent(
    uiState: RouteTrackingUiState,
    modifier: Modifier = Modifier,
    onStartTracking: () -> Unit
) {
    val context = LocalContext.current
    val cameraPositionState = rememberCameraPositionState()

    val mapStyleOptions = remember {
        MapStyleOptions.loadRawResourceStyle(context, R.raw.map_style_dark)
    }

    // 追蹤時，鏡頭跟隨目前位置
    LaunchedEffect(uiState.currentPosition) {
        uiState.currentPosition?.let {
            if (uiState.isTracking) {
                // 追蹤時，鏡頭保持在縮放級別 17 處跟隨目前位置
                cameraPositionState.animate(
                    CameraUpdateFactory.newLatLngZoom(it, 17f)
                )
            } else if (uiState.userPath.size > 1 && uiState.endLocation == it) {
                // 追蹤結束時，縮放到完整路線
                val boundsBuilder = com.google.android.gms.maps.model.LatLngBounds.builder()
                uiState.userPath.forEach { point -> boundsBuilder.include(point) }
                cameraPositionState.animate(
                    CameraUpdateFactory.newLatLngBounds(boundsBuilder.build(), 100)
                )
            }
        }
    }

    Box(modifier = modifier.fillMaxSize()) {
        GoogleMap(
            modifier = Modifier.fillMaxSize(),
            cameraPositionState = cameraPositionState,
            properties = MapProperties(
                isMyLocationEnabled = true,
                mapStyleOptions = mapStyleOptions
            ),
            uiSettings = MapUiSettings(
                myLocationButtonEnabled = false,
                zoomControlsEnabled = true // 保持 Zoom Controls
            )
        ) {
            // 繪製軌跡線
            if (uiState.userPath.size > 1) {
                Polyline(
                    points = uiState.userPath,
                    color = Color(0xFF448AFF),
                    width = 20f
                )
            }

            // 標記起點 (追蹤開始後固定不動)
            uiState.startLocation?.let { start ->
                Marker(
                    state = MarkerState(position = start),
                    title = "起點",
                    icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_GREEN)
                )
            }

            // 標記終點 (只有在追蹤停止時才標記)
            if (!uiState.isTracking) {
                uiState.endLocation?.let { end ->
                    Marker(
                        state = MarkerState(position = end),
                        title = "終點",
                        icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED)
                    )
                }
            }
        }

        // 顯示頂部資訊卡片
        TopTrackingInfoCard(
            totalDistance = uiState.totalDistance,
            isTracking = uiState.isTracking,
            modifier = Modifier.align(Alignment.TopCenter).padding(top = 16.dp)
        )

        // 顯示錯誤訊息 (如權限不足)
        uiState.locationError?.let { error ->
            Snackbar(
                modifier = Modifier.align(Alignment.BottomCenter).padding(16.dp),
                action = {
                    TextButton(onClick = onStartTracking) { Text("重試") }
                }
            ) {
                Text("位置錯誤: ${error}", color = Color.White)
            }
        }
    }
}

@Composable
private fun TopTrackingInfoCard(totalDistance: Float, isTracking: Boolean, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier.fillMaxWidth(0.85f),
        colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.95f)),
        elevation = CardDefaults.cardElevation(8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = if (isTracking) "正在追蹤..." else "追蹤已停止",
                style = MaterialTheme.typography.titleMedium,
                color = if (isTracking) Color(0xFF4CAF50) else Color.Red
            )
            Spacer(modifier = Modifier.height(4.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = String.format("%.2f", totalDistance),
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(text = "公里", style = MaterialTheme.typography.titleMedium, color = Color.Gray)
            }
        }
    }
}