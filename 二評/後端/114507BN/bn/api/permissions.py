# api/permissions.py

"""
本檔案定義了專案中使用的自訂權限類別 (Custom Permissions)。

這些權限類別用於 Django REST Framework 的 View 中，以實現更精細的物件級存取控制，
確保只有授權的使用者才能對特定資料進行操作。
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import GroupMember

class IsOwnerOrAdmin(BasePermission):
    """
    自訂權限：僅允許物件的擁有者 (owner) 或網站管理員 (staff) 進行操作。

    - 適用於 `Trip`, `UserProfile` 等具有直接使用者關聯的模型。
    - 會自動檢查 `obj.personnel` 或 `obj.user` 是否等於 `request.user`。
    """
    def has_object_permission(self, request, view, obj):
        # 網站管理員擁有所有權限
        if request.user and request.user.is_staff:
            return True

        # 檢查請求的使用者是否為物件的擁有者
        # 使用 getattr 安全地獲取擁有者屬性，使其能兼容不同模型
        owner = getattr(obj, 'personnel', getattr(obj, 'user', None))
        return owner == request.user


class IsGroupOwnerOrAdmin(BasePermission):
    """
    自訂權限：針對 `Group` 物件的二級權限管理。

    - **讀取權限 (GET, HEAD, OPTIONS)**: 任何群組內的成員或網站管理員皆可。
    - **寫入權限 (POST, PUT, PATCH, DELETE)**: 僅限以下三種角色：
        1. 群組的建立者 (`created_by`)
        2. 群組的管理員 (`role='ADMIN'`)
        3. 網站管理員 (`is_staff`)
    """
    def has_object_permission(self, request, view, obj):
        # 對於非認證使用者，不授予任何權限
        if not request.user.is_authenticated:
            return False

        # 讀取權限：是群組成員或網站管理員即可
        if request.method in SAFE_METHODS:
            is_member = GroupMember.objects.filter(group=obj, user=request.user).exists()
            return is_member or request.user.is_staff

        # 寫入權限：必須是建立者、群組管理員或網站管理員
        is_owner = (obj.created_by == request.user)
        is_group_admin = GroupMember.objects.filter(
            group=obj,
            user=request.user,
            role='ADMIN'
        ).exists()

        return is_owner or request.user.is_staff or is_group_admin


class IsAnnouncementPublisherOrAdmin(BasePermission):
    """
    自訂權限：針對 `GroupAnnouncement` 物件的權限管理。

    - **讀取權限 (GET, HEAD, OPTIONS)**: 允許任何人。
    - **寫入權限 (POST, PUT, PATCH, DELETE)**: 僅限以下三種角色：
        1. 公告的發布者 (`publisher`)
        2. 公告所屬群組的管理員 (`role='ADMIN'`) 或建立者
        3. 網站管理員 (`is_staff`)
    """
    def has_object_permission(self, request, view, obj):
        # 讀取權限：允許任何人
        if request.method in SAFE_METHODS:
            return True

        # 對於非認證使用者，不授予寫入權限
        if not request.user.is_authenticated:
            return False

        # 寫入權限檢查
        is_publisher = (obj.publisher == request.user)
        is_group_creator = (obj.group.created_by == request.user)
        is_group_admin = GroupMember.objects.filter(
            group=obj.group,
            user=request.user,
            role='ADMIN'
        ).exists()

        return is_publisher or is_group_creator or is_group_admin or request.user.is_staff