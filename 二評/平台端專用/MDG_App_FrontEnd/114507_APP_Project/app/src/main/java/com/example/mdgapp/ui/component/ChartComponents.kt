package com.example.mdgapp.ui.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChartFilterMenus(
    timeUnitOptions: List<String>,
    selectedTimeUnit: String,
    valueOptions: List<String>,
    selectedValue: String,
    onTimeUnitSelected: (String) -> Unit,
    onValueSelected: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val darkThemeColors = TextFieldDefaults.colors(
        focusedTextColor = Color.White,
        unfocusedTextColor = Color.White,
        focusedTrailingIconColor = Color.White,
        unfocusedTrailingIconColor = Color.White,
        focusedContainerColor = Color.Gray.copy(alpha = 0.3f),
        unfocusedContainerColor = Color.Gray.copy(alpha = 0.3f),
        cursorColor = Color.White,
        focusedIndicatorColor = Color.Transparent,
        unfocusedIndicatorColor = Color.Transparent,
        disabledIndicatorColor = Color.Transparent
    )

    var isTimeUnitExpanded by remember { mutableStateOf(false) }
    var isValueExpanded by remember { mutableStateOf(false) }

    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        ExposedDropdownMenuBox(
            expanded = isTimeUnitExpanded,
            onExpandedChange = { isTimeUnitExpanded = it },
            modifier = Modifier.weight(1f)
        ) {
            OutlinedTextField(
                value = selectedTimeUnit,
                onValueChange = {},
                readOnly = true,
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = isTimeUnitExpanded) },
                colors = darkThemeColors,
                modifier = Modifier.menuAnchor()
            )
            ExposedDropdownMenu(
                expanded = isTimeUnitExpanded,
                onDismissRequest = { isTimeUnitExpanded = false }
            ) {
                timeUnitOptions.filter { it != selectedTimeUnit }.forEach { option ->
                    DropdownMenuItem(
                        text = { Text(option) },
                        onClick = {
                            onTimeUnitSelected(option)
                            isTimeUnitExpanded = false
                        }
                    )
                }
            }
        }

        ExposedDropdownMenuBox(
            expanded = isValueExpanded,
            onExpandedChange = { isValueExpanded = it },
            modifier = Modifier.weight(1f)
        ) {
            OutlinedTextField(
                value = selectedValue,
                onValueChange = {},
                readOnly = true,
                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = isValueExpanded) },
                colors = darkThemeColors,
                modifier = Modifier.menuAnchor()
            )
            ExposedDropdownMenu(
                expanded = isValueExpanded,
                onDismissRequest = { isValueExpanded = false }
            ) {
                valueOptions.forEach { option ->
                    DropdownMenuItem(
                        text = { Text(option) },
                        onClick = {
                            onValueSelected(option)
                            isValueExpanded = false
                        }
                    )
                }
            }
        }
    }
}