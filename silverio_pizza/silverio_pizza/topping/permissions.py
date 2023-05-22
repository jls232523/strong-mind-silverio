from rest_framework.permissions import BasePermission


class IsChefUser(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a chef user
        return request.user.is_authenticated and request.user.is_chef


class IsOwnerUser(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is an owner user
        return request.user.is_authenticated and request.user.is_owner
