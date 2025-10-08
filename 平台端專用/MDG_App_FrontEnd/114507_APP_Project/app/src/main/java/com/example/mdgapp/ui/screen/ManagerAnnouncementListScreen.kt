package com.example.mdgapp.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.Announcement
import com.example.mdgapp.data.viewmodel.ManagerAnnouncementViewModel
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerAnnouncementListScreen(
    navController: NavController,
    viewModel: ManagerAnnouncementViewModel = viewModel()
) {
    val announcements by viewModel.announcements.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("公告列表") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回")
                    }
                },
                actions = {
                    IconButton(onClick = { navController.navigate("managerAddAnnouncement") }) {
                        Icon(Icons.Default.Add, "新增公告")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Black,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White,
                    actionIconContentColor = Color.White
                )
            )
        },
        containerColor = Color.Black
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier.padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(announcements, key = { it.id }) { announcement ->
                AnnouncementListItem(
                    announcement = announcement,
                    onClick = {
                        navController.navigate("managerEditAnnouncement/${announcement.id}")
                    }
                )
            }
        }
    }
}

@Composable
fun AnnouncementListItem(announcement: Announcement, onClick: () -> Unit = {}) {
    Card(
        onClick = onClick,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A2A2E)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(Modifier.padding(16.dp)) {
            Text(announcement.subject, color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Text(announcement.content, color = Color.LightGray, fontSize = 14.sp, maxLines = 3)
            Spacer(Modifier.height(8.dp))
            Text(
                "發佈於: ${announcement.publishDate.format(DateTimeFormatter.ofPattern("yyyy-MM-dd"))}",
                color = Color.Gray,
                fontSize = 12.sp
            )
        }
    }
}