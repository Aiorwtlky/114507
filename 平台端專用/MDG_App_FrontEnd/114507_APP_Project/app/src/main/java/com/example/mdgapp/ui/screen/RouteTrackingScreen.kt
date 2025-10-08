// 檔案路徑: app/src/main/java/com/example/mdgapp/ui/screen/RouteTrackingScreen.kt
package com.example.mdgapp.ui.screen
/*
import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.R
import com.example.mdgapp.data.viewmodel.RouteTrackingUiState
import com.example.mdgapp.data.viewmodel.RouteTrackingViewModel
import com.example.mdgapp.ui.component.InfoCardText
import com.example.mdgapp.util.formatHoursDecimal
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.LatLngBounds
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

    // ✅ 移除 Scaffold 和 FloatingActionButton，因為不再需要開始/停止按鈕
    if (hasLocationPermission) {
        MapWithBottomSheet(
            uiState = uiState
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


@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun MapWithBottomSheet(uiState: RouteTrackingUiState, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val scaffoldState = rememberBottomSheetScaffoldState()
    val cameraPositionState = rememberCameraPositionState()

    val mapStyleOptions = remember {
        MapStyleOptions.loadRawResourceStyle(context, R.raw.map_style_dark)
    }

    // ✅ 關鍵修改：當地圖路徑載入後，自動縮放到最佳視野
    LaunchedEffect(uiState.userPath) {
        if (uiState.userPath.isNotEmpty()) {
            val boundsBuilder = LatLngBounds.builder()
            uiState.userPath.forEach { point ->
                boundsBuilder.include(point)
            }
            // 100 是邊界留白 (padding) 的像素值
            cameraPositionState.animate(
                CameraUpdateFactory.newLatLngBounds(boundsBuilder.build(), 100)
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
            properties = MapProperties(
                isMyLocationEnabled = true, // 仍然可以顯示使用者自己的藍點位置
                mapStyleOptions = mapStyleOptions
            ),
            uiSettings = MapUiSettings(
                myLocationButtonEnabled = true,
                zoomControlsEnabled = false
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

            // ✅ 簡化標記：只顯示固定的起點和終點
            uiState.startLocation?.let { start ->
                Marker(
                    state = MarkerState(position = start),
                    title = "起點",
                    icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_GREEN)
                )
            }
            uiState.endLocation?.let { end ->
                Marker(
                    state = MarkerState(position = end),
                    title = "終點",
                    icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED)
                )
            }
        }
    }
}

// ... (StatisticsContent Composable 保持不變)*/