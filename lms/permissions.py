from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    """
    True если пользователь в группе moderators.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name="moderators").exists()
        )


class IsOwner(BasePermission):
    """
    Object-level permission: доступ только владельцу объекта.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(obj, "owner_id", None) == user.id
        )
