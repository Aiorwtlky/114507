package com.example.mdgapp.ui.screen

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.mdgapp.data.viewmodel.ManagerAnnouncementViewModel
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManagerAddAnnouncementScreen(
    navController: NavController,
    announcementId: Int? = null,
    viewModel: ManagerAnnouncementViewModel = viewModel()
) {
    val isEditing = announcementId != null

    LaunchedEffect(announcementId) {
        if (isEditing) {
            viewModel.loadAnnouncementForEditing(announcementId!!)
        } else {
            viewModel.resetNewAnnouncementState()
        }
    }

    val state by viewModel.newAnnouncementState.collectAsState()
    val isFormValid = state.subject.isNotBlank() && state.content.isNotBlank()
    var showDatePicker by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (isEditing) "編輯公告" else "新增公告") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "返回")
                    }
                },
                actions = {
                    TextButton(
                        onClick = {
                            if (isEditing) {
                                viewModel.updateAnnouncement()
                            } else {
                                viewModel.publishAnnouncement()
                            }
                            navController.navigateUp()
                        },
                        enabled = isFormValid
                    ) {
                        Text(if (isEditing) "更新" else "發佈")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Black,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        },
        containerColor = Color.Black
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text("發佈單位: 總部車隊 / 王大明 (管理者)", color = Color.Gray, fontSize = 14.sp)

            OutlinedTextField(
                value = state.subject,
                onValueChange = { viewModel.onSubjectChange(it) },
                label = { Text("主旨") },
                modifier = Modifier.fillMaxWidth()
            )

            Column {
                Text("發佈日期", color = Color.White, fontWeight = FontWeight.Medium)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    RadioButton(selected = !state.isScheduled, onClick = { viewModel.onPublishOptionChange(false) })
                    Text("即時發佈", color = Color.White, modifier = Modifier.clickable { viewModel.onPublishOptionChange(false) })
                    Spacer(Modifier.width(16.dp))
                    RadioButton(selected = state.isScheduled, onClick = { viewModel.onPublishOptionChange(true) })
                    Text("排定時程", color = Color.White, modifier = Modifier.clickable { viewModel.onPublishOptionChange(true) })
                }
                AnimatedVisibility(visible = state.isScheduled) {
                    Button(onClick = { showDatePicker = true }) {
                        Text("選擇日期: ${state.scheduledDate}")
                    }
                }
            }

            OutlinedTextField(
                value = state.content,
                onValueChange = { viewModel.onContentChange(it) },
                label = { Text("內容") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
            )
        }
    }

    if (showDatePicker) {
        val datePickerState = rememberDatePickerState(
            initialSelectedDateMillis = state.scheduledDate.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
        )
        DatePickerDialog(
            onDismissRequest = { showDatePicker = false },
            confirmButton = {
                TextButton(onClick = {
                    datePickerState.selectedDateMillis?.let {
                        val selectedDate = Instant.ofEpochMilli(it).atZone(ZoneId.systemDefault()).toLocalDate()
                        viewModel.onDateSelected(selectedDate)
                    }
                    showDatePicker = false
                }) { Text("確定") }
            },
            dismissButton = { TextButton(onClick = { showDatePicker = false }) { Text("取消") } }
        ) {
            DatePicker(state = datePickerState)
        }
    }
}