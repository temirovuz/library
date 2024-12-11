from rest_framework import permissions


class IsAmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'admin':
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
