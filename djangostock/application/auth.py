from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class UnauthenticatedPost(BasePermission):
    """
    Permission to always allow POST.
    """

    def has_permission(self, request, view):
        return request.method in ["POST"]


class IsHimself(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.

        return obj.id == request.user.id
