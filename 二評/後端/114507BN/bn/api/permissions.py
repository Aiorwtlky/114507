# api/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import GroupMember # 【新增】

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
    自訂權限：只允許群組的建立者 (created_by) 或管理員 (admin) 進行編輯或刪除。
    """
    def has_object_permission(self, request, view, obj):
        # 任何已登入的使用者都有讀取權限
        if request.method in SAFE_METHODS:
            # 【優化】更精確的權限：必須是群組成員才能查看
            return GroupMember.objects.filter(group=obj, user=request.user).exists() or request.user.is_staff
        
        # 寫入權限只開放給物件的擁有者或管理員
        return obj.created_by == request.user or request.user.is_staff

# --- 【新增這個 Class】 ---
class IsAnnouncementPublisherOrAdmin(BasePermission):
    """
    自訂權限：只允許公告的發布者 (publisher) 或管理員 (admin) 進行編輯或刪除。
    """
    def has_object_permission(self, request, view, obj):
        # 讀取權限開放給所有人 (因為查看群組時就會看到公告)
        if request.method in SAFE_METHODS:
            return True
        
        # 寫入權限只開放給發布者或管理員
        return obj.publisher == request.user or request.user.is_staff