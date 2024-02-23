from rest_framework import permissions
from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly


class IsAdminIsOwnerOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated or request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.author == user or user.is_staff or request.method in permissions.SAFE_METHODS


class IsAdminIsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.author == user and user.is_staff
