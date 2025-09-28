// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/RouteTrackingScreen.kt
package com.example.mdgapp.ui.screen

import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.RouteTrackingUiState
import com.example.mdgapp.data.viewmodel.RouteTrackingViewModel
import com.example.mdgapp.ui.component.InfoCardText
import com.example.mdgapp.util.formatHoursDecimal
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
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
            FloatingActionButton(onClick = { viewModel.toggleTracking() }) {
                Icon(
                    imageVector = if (uiState.isTracking) Icons.Default.Pause else Icons.Default.PlayArrow,
                    contentDescription = if (uiState.isTracking) "停止" else "開始"
                )
            }
        },
        floatingActionButtonPosition = FabPosition.Center
    ) { paddingValues ->
        if (hasLocationPermission) {
            MapWithBottomSheet(
                uiState = uiState,
                modifier = Modifier.padding(paddingValues)
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


@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun MapWithBottomSheet(uiState: RouteTrackingUiState, modifier: Modifier = Modifier) {
    val scaffoldState = rememberBottomSheetScaffoldState()
    val cameraPositionState = rememberCameraPositionState {
        position = CameraPosition.fromLatLngZoom(LatLng(25.047924, 121.517082), 15f) // 預設台北車站
    }

    LaunchedEffect(uiState.currentLocation) {
        uiState.currentLocation?.let {
            cameraPositionState.animate(
                update = CameraUpdateFactory.newLatLngZoom(it, 17f),
                durationMs = 1000
            )
        }
    }

    BottomSheetScaffold(
        modifier = modifier,
        scaffoldState = scaffoldState,
        sheetPeekHeight = 180.dp,
        sheetContent = {
            StatisticsContent(
                totalDistance = uiState.totalDistance,
                time = uiState.time
            )
        }
    ) { paddingValues ->
        GoogleMap(
            modifier = Modifier.fillMaxSize().padding(paddingValues),
            cameraPositionState = cameraPositionState,
            properties = MapProperties(isMyLocationEnabled = !uiState.isTracking), // 模擬時可關閉藍點
            uiSettings = MapUiSettings(
                myLocationButtonEnabled = true,
                zoomControlsEnabled = false
            )
        ) {
            if (uiState.userPath.isNotEmpty()) {
                Polyline(
                    points = uiState.userPath,
                    color = Color.Blue,
                    width = 15f
                )
            }
            uiState.currentLocation?.let {
                Marker(
                    state = MarkerState(position = it),
                    title = "目前位置"
                )
            }
        }
    }
}


@Composable
private fun StatisticsContent(totalDistance: Float, time: Int) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFF1C1C1E))
            .padding(16.dp)
    ) {
        Text("統計資訊", fontSize = 20.sp, color = Color.White)
        Spacer(Modifier.height(12.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            InfoCardText(
                valueText = formatHoursDecimal(time),
                label = "行車時長",
                fillColor = Color(0xFF2196F3),
                backgroundColor = Color(0x552196F3),
                progressValue = time / 3600f,
                maxProgress = 8f,
                modifier = Modifier.weight(1f)
            )
            InfoCardText(
                valueText = String.format("%.2f km", totalDistance),
                label = "公里數",
                fillColor = Color(0xFFF48FB1),
                backgroundColor = Color(0x55F48FB1),
                progressValue = totalDistance,
                maxProgress = 100f,
                modifier = Modifier.weight(1f)
            )
        }
    }
}