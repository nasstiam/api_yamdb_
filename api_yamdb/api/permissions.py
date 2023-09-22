from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorModeratorAdminSuperuserOrReadOnly(BasePermission):
    """ Author, moderator, admin, superuser are permitted to change or delete object"""
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author
                or request.user.is_superuser
                or request.user.is_admin
                or request.user.is_moderator
                )

class IsAdminOrReadOnly(BasePermission):
    """ Only admin is permitted to create, change or delete object"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)


class IsAdminOnly(BasePermission):
    """ Only admin and superuser are permitted to get user's info"""
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_superuser
