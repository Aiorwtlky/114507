package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.MyLocation
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.data.viewmodel.RouteTrackingViewModel
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.LatLngBounds
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.maps.android.compose.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RouteTrackingScreen(
    navController: NavController,
    viewModel: RouteTrackingViewModel
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    val cameraPositionState = rememberCameraPositionState()
    val coroutineScope = rememberCoroutineScope()

    val startLocation = uiState.startLocation

    // 處理地圖相機移動邏輯 (在數據載入完成後，縮放地圖到完整路線)
    LaunchedEffect(uiState.userPath) {
        if (!uiState.isLoading && uiState.userPath.size > 1) {
            val boundsBuilder = LatLngBounds.builder()
            uiState.userPath.forEach { point -> boundsBuilder.include(point) }

            cameraPositionState.animate(
                CameraUpdateFactory.newLatLngBounds(boundsBuilder.build(), 100),
                durationMs = 1500
            )
        }
    }

    // 處理定位到起點的點擊事件
    val onLocateStartPoint = {
        if (startLocation != null) {
            coroutineScope.launch {
                cameraPositionState.animate(
                    CameraUpdateFactory.newLatLngZoom(startLocation, 16f),
                    durationMs = 800
                )
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("行駛軌跡總覽") },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.White),
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "返回"
                        )
                    }
                }
            )
        },
        floatingActionButton = {
            if (startLocation != null) {
                FloatingActionButton(
                    onClick = onLocateStartPoint,
                    containerColor = Color.White,
                    contentColor = Color(0xFF448AFF)
                ) {
                    Icon(
                        imageVector = Icons.Default.MyLocation,
                        contentDescription = "定位到起點"
                    )
                }
            }
        },
        floatingActionButtonPosition = FabPosition.End,
        bottomBar = {
            StatisticsContent(
                totalDistance = uiState.totalDistance,
                time = uiState.time
            )
        }
    ) { paddingValues ->
        Box(modifier = Modifier.fillMaxSize().padding(paddingValues)) {

            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }
                uiState.userPath.isNotEmpty() -> {
                    GoogleMap(
                        modifier = Modifier.fillMaxSize(),
                        cameraPositionState = cameraPositionState,
                        properties = MapProperties(
                            isMyLocationEnabled = false,
                            mapStyleOptions = MapStyleOptions.loadRawResourceStyle(context, R.raw.map_style_dark)
                        ),
                        uiSettings = MapUiSettings(
                            myLocationButtonEnabled = false,
                            // ⭐ 修正點: 移除放大縮小按鍵
                            zoomControlsEnabled = false
                        )
                    ) {
                        // 繪製軌跡線
                        Polyline(
                            points = uiState.userPath,
                            color = Color(0xFF448AFF),
                            width = 20f
                        )

                        // 繪製起點和終點標記
                        uiState.startLocation?.let { start ->
                            Marker(
                                state = MarkerState(position = start),
                                title = "起點 (善導寺)",
                                icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_GREEN)
                            )
                        }
                        uiState.endLocation?.let { end ->
                            Marker(
                                state = MarkerState(position = end),
                                title = "終點 (台北車站)",
                                icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED)
                            )
                        }
                    }
                }
                else -> {
                    Text(
                        "無法載入軌跡數據",
                        color = Color.Red,
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
            }
        }
    }
}

// 統計數據容器
@Composable
private fun StatisticsContent(totalDistance: Float, time: Int) {
    val hours = time / 3600
    val minutes = (time % 3600) / 60
    val seconds = time % 60
    val formattedTime = String.format("%02d:%02d:%02d", hours, minutes, seconds)

    Surface(
        color = Color.White,
        shadowElevation = 8.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp, vertical = 16.dp),
            horizontalArrangement = Arrangement.SpaceAround
        ) {
            StatisticsItem(
                value = String.format("%.2f", totalDistance),
                label = "總里程 (km)",
                color = Color(0xFF4CAF50)
            )
            StatisticsItem(
                value = formattedTime,
                label = "總時間",
                color = Color(0xFF2196F3)
            )
        }
    }
}

@Composable
private fun StatisticsItem(value: String, label: String, color: Color) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = Color.Gray
        )
    }
}