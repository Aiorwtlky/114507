# My Driving God DB - 後端資料庫結構說明

## 1. 總覽

本系統後端採用 Django 框架，並遵循其 ORM (Object-Relational Mapping) 設計模式。所有資料模型 (Models) 皆定義於 `api/models.py` 檔案中。

資料庫核心圍繞著**「人員 (User)」、「群組 (Group)」**與**「行程 (Trip)」**這三個主要實體展開，並透過多張關聯表與紀錄表，建構出一個完整的車隊安全管理系統。

---

## 2. 核心模型 (Core Models)

### 2.1 人員與權限管理 (User & Permission Management)

#### `User` (由 Django 內建)
- **用途**: 系統最基本的帳號單位，處理登入、密碼、身分驗證等。

#### `PersonnelProfile` (人員詳細資料)
- **用途**: 一對一擴充 `User` 模型，用以儲存與駕駛員職務相關的額外資訊。
- **關聯**: `OneToOneField` to `User`.

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `user` | OneToOneField | 關聯至 Django 內建的 User 模型。 | **主鍵 (Primary Key)** |
| `personnel_number` | CharField | 人員編號 (例如：員工編號)。 | `unique=True` |
| `gender` | CharField | 性別。 | 使用 `choices` 約束 |
| `avatar` | ImageField | 個人頭像圖片的路徑。 | |
| `phone` | CharField | 聯絡電話。 | |
| `license_type`| CharField | 駕照等級 (例如：職業大客車)。 | |
| `driving_experience` | PositiveIntegerField | 駕駛年資 (年)。 | |

#### `Group` (群組)
- **用途**: 組織與管理使用者的單位，例如「北區A組」。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `name` | CharField | 群組的顯示名稱。 | |
| `group_number` | CharField | 群組的唯一編號。 | `unique=True` |
| `created_by` | ForeignKey | 建立此群組的使用者。 | `related_name='owned_groups'` |
| `members` | ManyToManyField| 此群組包含的所有成員。 | 透過 `GroupMember` 中介表 |

#### `GroupMember` (群組成員)
- **用途**: `User` 與 `Group` 之間的多對多「中介表」，用於定義成員在特定群組中的角色。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `group` | ForeignKey | 關聯至 `Group`。 | |
| `user` | ForeignKey | 關聯至 `User`。 | |
| `role` | CharField | 在此群組中的角色。 | `MEMBER` 或 `ADMIN` |
| `joined_at` | DateTimeField| 成員加入群組的時間。 | |

---

### 2.2 車輛與行程管理 (Vehicle & Trip Management)

#### `VehicleDevice` (車機設備)
- **用途**: 記錄安裝在車輛上的硬體設備資訊。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `device_number` | CharField | 車機的唯一識別碼。 | `unique=True` |
| `vehicle_type` | CharField | 車輛類型 (例如：貨車、轎車)。 | |
| `is_active` | BooleanField| 此設備是否仍在服役。 | |

#### `Trip` (行程)
- **用途**: 系統的**核心記錄**，代表一趟完整的駕駛過程。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `trip_number` | CharField | 該趟行程的唯一識別碼。 | `unique=True` |
| `name` | CharField | 使用者可自訂的行程名稱。 | |
| `personnel` | ForeignKey | 執行此趟行程的駕駛員。 | 關聯至 `User` |
| `group` | ForeignKey | 執行此趟行程時所屬的群組。 | 關聯至 `Group` |
| `device` | ForeignKey | 使用的車機設備。 | 關聯至 `VehicleDevice` |
| `start_time` | DateTimeField| 行程開始時間。 | |
| `end_time` | DateTimeField| 行程結束時間。 | |
| `score` | DecimalField | **最終計算出的行程總分**。 | 由 `calculate_trip_score` 服務計算 |
| `in_car_score`| DecimalField | A類 (車內) 違規的類別分數。 | 由 `calculate_trip_score` 服務計算 |
| `out_car_score`| DecimalField | B類 (車外) 違規的類別分數。 | 由 `calculate_trip_score` 服務計算 |
| `ai_suggestion`| TextField | AI 根據此趟行程生成的改善建議。| 由 `generate_ai_suggestion` 服務生成 |

#### `ScoringStandard` (評分標準)
- **用途**: 定義所有危險駕駛事件的類型、編號與扣分標準。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `event_number`| CharField | 事件的唯一編號 (例如 `A01`, `B03`)。| `unique=True` |
| `description` | CharField | 事件的文字描述。 | 例如：「重度疲勞(閉眼5秒以上)」 |
| `deduction_points` | IntegerField| 觸發此事件在單一區間內的扣分。| |

#### `AiVisionLog` (AI 視覺事件紀錄)
- **用途**: 記錄在某趟行程中，由車機 AI 偵測到的**具體**危險駕駛事件。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `trip` | ForeignKey | 此事件發生在哪一趟行程中。 | `related_name='aivisionlog_set'` |
| `event` | ForeignKey | 此事件對應的評分標準類型。 | 關聯至 `ScoringStandard` |
| `timestamp` | DateTimeField| 事件發生的精確時間點。 | |
| `event_details`| CharField | 事件的額外細節 (例如：閉眼4秒)。| |

#### `VideoRecord` (影像紀錄)
- **用途**: 儲存與行程關聯的影像檔案資訊。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `trip` | ForeignKey | 此影像屬於哪一趟行程。 | `related_name='videorecord_set'` |
| `video_url` | URLField | 影片在雲端儲存的網址。 | |
| `start_time` | DateTimeField| 影片片段的開始時間。 | |
| `end_time` | DateTimeField| 影片片段的結束時間。 | |

---

### 2.3 系統與公告 (System & Announcement)

#### `ActivationCode` (系統啟用碼)
- **用途**: 用於新使用者註冊時的驗證，一個碼可供多人使用。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `code` | CharField | 啟用碼字串。 | `unique=True` |
| `max_uses` | PositiveIntegerField | 最大可使用次數。 | |
| `current_uses`| PositiveIntegerField | 目前已使用次數。 | |
| `expires_at`| DateTimeField | 啟用碼的過期時間。 | |

#### `InvitationCode` (群組邀請碼)
- **用途**: 用於邀請新成員直接加入特定群組，一個碼只能使用一次。

| 欄位名稱 | 資料類型 | 說明 | 重要關聯/備註 |
| :--- | :--- | :--- | :--- |
| `code` | CharField | 邀請碼字串。 | `unique=True` |
| `group` | ForeignKey | 使用此碼將會加入的群組。 | 關聯至 `Group` |
| `created_by`| ForeignKey | 建立此邀請碼的管理員。 | 關聯至 `User` |
| `is_used` | BooleanField | 此邀請碼是否已被使用。 | |

#### `SystemAnnouncement` (系統公告)
- **用途**: 由系統管理員發布，所有使用者都看得到的公告。

#### `GroupAnnouncement` (群組公告)
- **用途**: 由群組管理員發布，只有該群組的成員才看得到的公告。