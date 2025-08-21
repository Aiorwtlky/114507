package com.example.mdgapp.ui.component

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import com.example.mdgapp.R

@Composable
fun RouteMap(modifier: Modifier = Modifier) {
    Image(
        painter = painterResource(id = R.drawable.fake_map),
        contentDescription = "Static Map",
        contentScale = ContentScale.Crop,
        modifier = modifier
            .fillMaxWidth()
            .height(320.dp)
    )
}
