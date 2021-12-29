from rest_framework import permissions

ADMIN_METHODS = ('PATCH', 'DELETE')
SAFE_METHODS = ('GET', 'POST')


class IsAuthorAdminModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):

        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        if request.method == 'DELETE' or request.method == 'PATCH':
            if (request.user.is_admin
               or request.user.is_moderator
               or obj.author == request.user):
                return True
            return False
        return True


class IsAdminorUpdateReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_admin:
                if (request.method == "GET"
                        or request.method == "PATCH"
                        or request.method == "DELETE"
                        or request.method == "POST"):
                    return True
                return True
            if request.user.is_authenticated != request.user.is_admin:
                if request.method == "GET" or request.method == "PATCH":
                    return True
                if request.method == "POST":
                    return False
                return True
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return (obj.username == request.user.username
                or request.user.is_admin
                or request.user.is_moderator)


class AdminOrReadonly(permissions.BasePermission):
    message = "User not admin"

    def has_permission(self, request, view):

        if (
            request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and request.user.is_admin):
            return True
        return False
