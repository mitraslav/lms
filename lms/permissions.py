from rest_framework.permissions import BasePermission

class IsModer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.isauthenticated and
            user.groups.filter(name="moderators").exists()
        )