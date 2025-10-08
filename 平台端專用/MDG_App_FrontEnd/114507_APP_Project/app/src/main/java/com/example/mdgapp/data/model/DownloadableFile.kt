package com.example.mdgapp.data.model

/**
 * 表示一個可從遠端伺服器下載的檔案。
 *
 * @property id 檔案的唯一識別碼。
 * @property fileName 要向使用者顯示的檔案名稱。
 * @property downloadUrl 用於下載檔案的直接 URL。
 * @property fileSize 檔案的大小（以位元組為單位），可用於向使用者顯示。
 */
data class DownloadableFile(
    val id: String,
    val fileName: String,
    val downloadUrl: String,
    val fileSize: Long
)
