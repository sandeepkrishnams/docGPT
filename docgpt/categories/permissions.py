from rest_framework.permissions import BasePermission


class SuperuserPermission(BasePermission):
    """
    Custom permission class that allows access only to superusers.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser
