專案交接文件：吾駕仙智慧交通系統
文件版本：2.1
更新日期：2025-10-04

1. 專案總覽
「吾駕仙」是一套專注於駕駛行為的智慧分析系統，旨在透過即時監控、數據分析與 AI 回饋，提升職業駕駛員的行車安全。

本專案採用前後端分離的架構：
後端 (Backend)：使用 Django REST Framework 開發，負責處理所有商業邏輯、資料庫互動、使用者認證、權限管理以及與 AI 服務的溝通。
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



Pillow

圖片處理 (用於頭像上傳)

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
3.1. 資料庫模型 (api/models.py)
核心資料庫結構如下：
使用者與權限：
User: Django 內建使用者模型。
PersonnelProfile: 一對一擴充 User，包含頭像 (avatar)、電話、駕照等級等，是所有人員的詳細資料。
群組與角色：
Group: 定義一個群組，包含 created_by 欄位來標示「群組建立者」。
GroupMember: 作為 User 和 Group 之間的多對多關聯橋樑。新增了 role 欄位，區分 MEMBER (一般成員) 和 ADMIN (群組管理員)。
InvitationCode: 用於儲存有時效性、一次性的群組邀請碼。
核心數據：
Trip: 記錄每一趟行程的完整資訊，包含計算後的 score 和 ai_suggestion。
AiVisionLog: 記錄行程中的 AI 視覺偵測事件（如：急煞、分心）。
VideoRecord: 記錄影片相關資訊。
其他：
GroupAnnouncement: 儲存群組內的公告。
3.2. 核心 API 端點 (api/urls.py & api/views.py)
功能模組

HTTP 方法

端點

說明與權限

認證

POST

/api/token/

使用者登入，獲取 JWT Token。



POST

/api/auth/register/

註冊新使用者，支援頭像上傳與邀請碼。



GET, PATCH

/api/auth/profile/

讀取/更新個人資料。回傳包含 is_group_leader 和 administered_groups 列表。

群組管理

POST

/api/groups/

建立新群組，會自動將建立者設為第一位成員。



GET

/api/me/groups/

獲取當前使用者所屬或建立的所有群組列表。



GET

/api/groups/<id>/members/

獲取群組成員列表 (含平均分、角色與頭像)。



POST

/api/groups/<id>/invitations/

群組建立者或管理員可為群組生成邀請碼。



PATCH

/api/groups/<gid>/members/<uid>/role/

群組建立者或管理員可變更成員角色。

公告管理

POST

/api/groups/<id>/announcements/

群組建立者或管理員可發布公告。

數據查詢

GET

/api/trips/, /api/videos/

獲取行程/影片列表 (支援 ?user_id= 參數)。

AI 功能

POST

/api/chatbot/

AI 智慧客服。

3.3. 圖片上傳設定
使用者上傳的頭像等媒體檔案會被儲存在後端專案根目錄下的 /media/ 資料夾。
透過 settings.py 和主 urls.py 的設定，開發伺服器 (runserver) 能夠提供 /media/ 路徑下的檔案存取。
PersonnelProfileSerializer 已被修改，avatar 欄位會回傳包含 http://<domain>:<port> 的完整圖片 URL，供前端直接使用。
4. 前端 (Flask) 架構與現況
4.1. 核心邏輯 (app.py)
make_api_request(): 作為 API 請求的統一出口，自動處理 Authorization 標頭和 JWT Token 的過期刷新。
登入與跳轉邏輯:
群組建立者 (is_group_leader: true) 登入後，會被 admin_logic_redirect 直接導向到功能最完整的 group_leader_view。
一般使用者或被指派的管理員登入後，一律進入 dashboard。
4.2. 使用者流程
群組建立者 (created_by):
登入後直接進入 group_leader_view。
可在此頁面管理成員（含查看頭像）、發布公告、生成邀請碼、指派其他成員為 ADMIN。
被指派的管理員 (role: 'ADMIN'):
登入後進入個人 dashboard。
儀表板上會額外顯示「群組管理面板」。
可在此面板直接點擊按鈕，前往「發布公告」或「邀請成員」頁面，無需跳轉到另一個儀表板。
一般使用者 (role: 'MEMBER'):
透過組長/管理員提供的邀請碼，在註冊頁面上傳頭像並填寫資料即可加入群組。
登入後進入個人 dashboard，可查看個人資料（含自己的頭像）、所屬群組、行程記錄等，但看不到任何管理功能。
5. 待辦事項與未來展望
前端串接:
完成 edit_profile.html 的頭像更新功能。
實現 dashboard.html 中「近期行程」的點擊跳轉功能 (trip_report 路由)。
為 group_leader_view.html 中的公告列表加上「編輯/刪除」按鈕的實際功能。
完成 member_dashboard.html 等使用者詳情頁面的開發。
後端功能:
權限細化: 目前 ADMIN 和 created_by 權限幾乎相同，未來可考慮區分，例如只有 created_by 能刪除群組。
資料操作: 為刪除公告、移除成員等敏感操作增加後端 API。
測試:
為後端的 api/ app 編寫單元測試與整合測試 (tests.py 目前為空)。
生產環境部署:
規劃將 Django 後端 (使用 Gunicorn/Nginx) 和 Flask 前端部署到正式伺服器。
