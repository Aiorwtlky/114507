buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        // 使用 libs 中的 kotlin 版本，確保版本同步
        classpath("org.jetbrains.kotlin:kotlin-serialization:${libs.versions.kotlin.get()}")
    }
}

plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
    // 2. 移除之前所有關於 kotlinSerialization 的宣告
}   