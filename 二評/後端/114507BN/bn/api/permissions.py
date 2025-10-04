# api/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import GroupMember
class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admin staff to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        if hasattr(obj, 'personnel'):
            return obj.personnel == request.user
        if hasattr(obj, 'user'):
             return obj.user == request.user
        return False

class IsGroupOwnerOrAdmin(BasePermission):
    """
    自訂權限：允許群組的建立者(created_by)、群組管理員(role='ADMIN')或網站管理員(admin)進行編輯或刪除。
    """
    def has_object_permission(self, request, view, obj):
        # 讀取權限：維持不變，是群組成員就可以看
        if request.method in SAFE_METHODS:
            return GroupMember.objects.filter(group=obj, user=request.user).exists() or request.user.is_staff
        
        # --- ▼▼▼ 修改寫入權限的檢查邏輯 ▼▼▼ ---
        if not request.user.is_authenticated:
            return False
            
        is_owner = (obj.created_by == request.user)
        is_staff = request.user.is_staff
        # 檢查請求的使用者是否為該群組的管理員
        is_group_admin = GroupMember.objects.filter(
            group=obj, 
            user=request.user, 
            role='ADMIN'
        ).exists()

        return is_owner or is_staff or is_group_admin
        # --- ▲▲▲ 修改結束 ▲▲▲ ---


class IsAnnouncementPublisherOrAdmin(BasePermission):
    """
    【修正後】
    自訂權限：允許公告的發布者、群組管理員(role='ADMIN')或網站管理員(admin)進行編輯或刪除。
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False

        # 檢查是否為公告發布者
        is_publisher = (obj.publisher == request.user)
        # 檢查是否為網站管理員
        is_staff = request.user.is_staff
        # 【新增】檢查是否為該公告所屬群組的管理員
        is_group_admin = GroupMember.objects.filter(
            group=obj.group, 
            user=request.user, 
            role='ADMIN'
        ).exists()

        return is_publisher or is_staff or is_group_admin