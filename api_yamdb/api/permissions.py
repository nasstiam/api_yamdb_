from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthorModeratorAdminSuperuserOrReadOnly(BasePermission):
    """ Author, moderator, admin, superuser are permitted to change or delete object"""
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author
                or request.user.role == 'moderator'
                or request.user.role == 'admin'
                or request.user.is_superuser
                )

class IsAdminOrReadOnly(BasePermission):
    """ Only admin is permitted to create, change or delete object"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            if request.user.is_authenticated:
                return request.user.role == 'admin'
            else:
                return False
