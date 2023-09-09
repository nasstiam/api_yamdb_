from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthorModeratorAdminSuperuserOrReadOnly(BasePermission):
    """ Author, moderator, admin, superuser are permitted to change or delete object"""
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author
                or request.user.role == 'moderator'
                or request.user.role == 'admin'
                or request.user.is_superuser is True)
