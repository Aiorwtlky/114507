專案交接文件：吾駕仙智慧交通系統
文件版本： 1.0
更新日期： 2025-10-03

1. 專案總覽
「吾駕仙」是一套專注於駕駛行為的智慧分析系統，旨在透過即時監控、數據分析與 AI 回饋，提升職業駕駛員的行車安全。

本專案採用前後端分離的架構：

後端 (Backend)：使用 Django REST Framework 開發，負責處理所有商業邏輯、資料庫互動、使用者認證以及與 AI 服務的溝通。

前端 (Frontend)：使用 Flask 框架作為伺服器，負責渲染使用者介面 (UI) 和處理與後端 API 的通訊。

2. 技術棧
類別

技術/函式庫

用途

後端

Django, Django REST Framework

核心框架，建構 RESTful API



djangorestframework-simplejwt

使用者認證 (JWT Token)



MySQL / PostgreSQL

資料庫 (由 .env 設定)



django-environ

環境變數管理



Hugging Face InferenceClient

AI 聊天與建議生成服務



WeasyPrint

動態生成 PDF 安全報告

前端

Flask

網頁伺服器與模板渲染



Jinja2

模板引擎



requests

與後端 API 通訊



HTML5 / CSS3 / JavaScript

使用者介面



Chart.js

數據視覺化圖表

環境

Python (venv)

虛擬環境



pip

套件管理

3. 後端 (Django) 架構與現況
後端專案提供了所有前端功能所需的 API 端點，並封裝了核心商業邏輯。

3.1. 專案啟動指南

建立並啟動 Python 虛擬環境 (venv)。

安裝依賴：pip install -r requirements.txt。

在專案根目錄建立 .env 檔案，並設定 SECRET_KEY, DATABASE_URL, HF_TOKEN。

執行資料庫遷移：python manage.py migrate。

建立超級管理員帳號：python manage.py createsuperuser。

啟動伺服器：python manage.py runserver (預設 port 8000)。

3.2. 核心資料庫模型 (api/models.py)

使用者與權限：

User: Django 內建使用者模型。

PersonnelProfile: 擴充使用者資訊，包含頭像 (avatar)、電話、駕照等級等。

群組與邀請：

Group: 定義一個群組，包含 created_by 欄位來標示「組長」。

GroupMember: 作為 User 和 Group 之間的多對多關聯橋樑。

InvitationCode: 用於儲存有時效性、一次性的群組邀請碼。

核心數據：

Trip: 記錄每一趟行程的完整資訊。

AiVisionLog: 記錄行程中的 AI 視覺偵測事件。

VideoRecord: 記錄影片相關資訊。

其他：

GroupAnnouncement: 儲存群組內的公告。

3.3. 已完成的核心 API 端點

功能模組

HTTP 方法

端點

說明

認證

POST

/api/token/

使用者登入，獲取 JWT Token



POST

/api/token/refresh/

刷新 Access Token



POST

/api/auth/register/

註冊新使用者 (可包含邀請碼)



GET, PATCH

/api/auth/profile/

讀取/更新個人資料，回傳包含 is_group_leader

群組管理

POST

/api/groups/

建立新群組



GET

/api/me/groups/

獲取當前使用者所屬的群組列表



GET, PUT, DELETE

/api/groups/<id>/

讀取、更新、刪除單一群組 (限組長)



GET

/api/groups/<id>/members/

獲取群組成員列表 (含平均分)



POST

/api/groups/<id>/invitations/

為群組生成邀請碼 (限組長)

公告管理

GET, POST

/api/groups/<id>/announcements/

讀取/建立群組公告 (限組長)



PUT, DELETE

/api/announcements/<id>/

更新/刪除單則公告 (限發布者)

數據查詢

GET

/api/trips/

獲取行程列表 (支援 ?user_id= 參數)



GET

/api/videos/

獲取影片列表 (支援 ?user_id= 參數)

報表與統計

GET

/api/statistics/trends/

獲取駕駛分數趨勢 (支援 ?user_id=)



GET

/api/trips/<id>/report/

動態生成 PDF 行程報告

AI 功能

POST

/api/chatbot/

AI 智慧客服

4. 前端 (Flask) 架構與現況
前端專案作為一個與使用者互動的介面，它本身不儲存任何業務數據，所有動態內容皆來自後端 API。

4.1. 專案啟動指南

建立並啟動 Python 虛擬環境 (venv)。

安裝依賴：pip install -r requirements.txt。

啟動伺服器：python app.py (預設 port 5000)。

4.2. 核心檔案與邏輯 (app.py)

make_api_request() 函式：這是整個前端的命脈，所有對後端 API 的請求都 через 此函式發出。它會自動處理：

在請求標頭 (Header) 中加入 Authorization: Bearer <access_token>。

當 API 回傳 401 Unauthorized (Token 過期) 時，自動使用 refresh_token 去請求新的 access_token，並重試原來的請求。

角色導向的跳轉：login 和 admin_logic_redirect 路由協同工作，實現了：

使用者登入後，向後端 /api/auth/profile/ 請求身份。

如果回傳的 is_group_leader 為 True，則跳轉至組長專用的儀表板 (/group_leader_view/<id>)。

否則，跳轉至一般使用者的儀表板 (/dashboard)。

路由 (Routing)：app.py 中定義了所有使用者可見的頁面 URL，並在每個路由函式中呼叫 make_api_request 來獲取該頁面所需的數據，最後將數據傳遞給 HTML 模板進行渲染。

4.3. 模板結構 (templates/)

base.html: 網站的主佈局，包含了共用的頁首、頁尾、以及根據登入狀態切換的側邊欄。

dashboard.html: 一般使用者的儀表板。

group_leader_view.html: 組長的儀表板，特色是左側有一個可切換所管理群組的側邊欄。

login.html, register.html: 認證頁面，其中註冊頁已整合邀請碼欄位。

invite_member.html: 動態生成與顯示邀請碼的頁面。

create_group.html: 建立新群組的表單頁面。

5. 完整使用者流程
5.1. 組長 (管理者) 流程

由系統管理員在 Django 後台 (/admin/) 建立帳號，並將其設為某個群組的 Created by。

組長在前端登入。

系統判斷其 is_group_leader 為 True，自動跳轉至 group_leader_view 頁面。

在此頁面，組長可以：

在左側邊欄切換管理不同的群組。

查看群組成員列表及其平均分數。

發布、編輯、刪除公告。

點擊「新增成員」按鈕，進入 invite_member 頁面，生成邀請碼給新成員。

5.2. 一般使用者 (駕駛員) 流程

從組長處獲得 8 位數的邀請碼。

訪問前端的 /register 頁面，填寫所有個人資料，並在「邀請碼」欄位中輸入。

註冊成功後，後端會自動將其加入對應的群組。

在 /login 頁面登入。

系統判斷其 is_group_leader 為 False，跳轉至 /dashboard 一般儀表板。

在儀表板上，使用者可以查看自己的個人資訊、所屬群組、以及近期的行程記錄。

6. 待辦事項與未來展望
前端串接：完成剩餘靜態頁面 (如 edit_profile.html, group_settings.html 等) 的 API 串接工作。

檔案上傳：實作使用者頭像的檔案上傳與儲存邏輯。

權限細化：為特定操作增加更精細的權限檢查 (例如：只有組長才能訪問 invite_member 頁面)。

生產環境部署：規劃將 Django 後端 (使用 Gunicorn/Nginx) 和 Flask 前端部署到正式伺服器。

