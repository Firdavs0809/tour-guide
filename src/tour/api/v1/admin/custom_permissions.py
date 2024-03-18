from rest_framework import permissions
from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly


class IsAdminIsOwner(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.is_active:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (obj.admin == user and user.is_staff) or user.is_superuser


class IsAdminIsAuthenticatedIsTourOwner(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.is_staff and user.is_active:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.agency.admin == user and user.is_staff or user.is_superuser


class IsSuperUser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser
