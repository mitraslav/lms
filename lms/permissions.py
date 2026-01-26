from rest_framework.permissions import BasePermission

class IsModer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            user.groups.filter(name="moderators").exists()
        )

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated and getattr(obj, "owner_id", None) == request.user.id)