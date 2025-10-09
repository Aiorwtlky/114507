# 專案名稱：AI 駕駛行為分析與車隊管理系統後端模型

## 概述 (Overview)

本文件描述了後端服務的核心 **Django 資料模型**，主要用於支援 **車隊管理、駕駛行為分析** 及 **AI 視覺事件紀錄** 等功能。系統圍繞著 **人員、群組、車機、行程** 等核心實體設計，旨在提供一個結構化的資料基礎來進行數據收集、評分、分析與回饋。

所有模型定義於 `api/models.py` 檔案中。

## 資料模型結構總覽 (Data Model Structure)

系統模型可分為四大主要模組：

1.  **人員與權限管理 (User & Permission Management)**
    * 管理使用者資料、群組與群組內角色。
2.  **系統與公告 (System & Announcement)**
    * 管理系統級和群組級的公告，以及群組邀請機制。
3.  **車輛與行程管理 (Vehicle & Trip Management)**
    * 本系統的核心模組，負責記錄行程細節、地理軌跡、AI 偵測事件、評分標準與影像紀錄。
4.  **回饋 (Feedback)**
    * 用於收集使用者對 AI 建議的意見回饋。

---

## 模組細節 (Module Details)

### 1. 人員與權限管理

| 模型名稱 (Table Name) | 說明 (Description) | 關鍵欄位 (Key Fields) | 關聯 (Relationship) |
| :--- | :--- | :--- | :--- |
| **PersonnelProfile** | 擴充 Django 內建 User 模型，儲存人員詳細資料。 | `personnel_number` (人員編號), `phone`, `license_number`, `driving_experience` (駕駛年資), `nfc_card_id` | **OneToOne** to `User` |
| **Group** | 定義使用者群組，用於組織成員和行程。 | `group_number`, `name`, `created_by` | **ManyToMany** to `User` via `GroupMember` |
| **GroupMember** | 群組與使用者之間的中介模型，定義成員角色。 | `group`, `user`, `role` (角色: 成員/管理員) | **ForeignKey** to `Group` & `User` |

### 2. 系統與公告

| 模型名稱 (Table Name) | 說明 (Description) | 關鍵欄位 (Key Fields) | 說明/邏輯 (Notes) |
| :--- | :--- | :--- | :--- |
| **SystemAnnouncement** | 平台級公告。 | `announcement_number`, `content`, `is_active` | - |
| **GroupAnnouncement** | 特定群組內部的公告。 | `announcement_number` (自動生成), `group`, `publisher` | `announcement_number` 邏輯：`ANN-{group_id}-{random_hex}` |
| **InvitationCode** | 具時效性、一次性的群組邀請碼。 | `code` (自動生成), `group`, `expires_at`, `is_used` | `code` 邏輯：`secrets.token_hex(4).upper()`；預設 24 小時過期。 |

### 3. 車輛與行程管理 (核心模組)

| 模型名稱 (Table Name) | 說明 (Description) | 關鍵欄位 (Key Fields) | 關聯 (Relationship) |
| :--- | :--- | :--- | :--- |
| **VehicleDevice** | 車載設備 (車機) 資料。 | `device_number`, `vehicle_type` | - |
| **Trip** | **核心行程紀錄**，記錄單次行程的整體資訊與評分。 | `trip_number`, `group`, `device`, `personnel`, `score`, `in_car_score`, `out_car_score`, `ai_suggestion`, `total_mileage` | **ForeignKey** to `Group`, `VehicleDevice`, `User` |
| **RouteLog** | 儲存行程中的**地理軌跡資料**。 | `trip`, `timestamp`, `location`, `speed` | **ForeignKey** to `Trip` |
| **ScoringStandard** | 定義 AI 偵測事件的**評分標準**。 | `event_number`, `description`, `deduction_points` (扣分點數) | - |
| **AiVisionLog** | 儲存 AI 偵測到的**具體駕駛事件紀錄**。 | `trip`, `event` (關聯評分標準), `timestamp`, `event_details`, `confidence_score` | **ForeignKey** to `Trip`, `ScoringStandard` |
| **VideoRecord** | 儲存與行程關聯的**影像紀錄資訊**。 | `video_number` (自動生成), `trip`, `video_url`, `start_time`, `end_time` | **ForeignKey** to `Trip` |

### 4. 回饋

| 模型名稱 (Table Name) | 說明 (Description) | 關鍵欄位 (Key Fields) | 邏輯 (Logic) |
| :--- | :--- | :--- | :--- |
| **TripSuggestionFeedback** | 收集使用者對 AI 行程建議的**回饋**。 | `trip`, `user`, `feedback_type` (1: 有幫助, -1: 沒有幫助), `comment` | **`unique_together = ('trip', 'user')`**：確保單一使用者對單一行程只提交一次回饋。 |

---

## 技術棧 (Technology Stack)

* **後端框架**: Django
* **資料庫 ORM**: Django Models
* **語言**: Python

---
