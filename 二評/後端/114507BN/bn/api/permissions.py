# api/permissions.py

from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admin staff to view/edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Admin users (is_staff=True) can access any object.
        if request.user and request.user.is_staff:
            return True
        
        # Check if the object has a 'personnel' attribute and if it matches the request user.
        # This works for models like Trip.
        if hasattr(obj, 'personnel'):
            return obj.personnel == request.user
        
        # Check if the object itself is the user.
        # This works for the User model itself (e.g., viewing a user's own profile).
        if hasattr(obj, 'user'):
             return obj.user == request.user

        return False