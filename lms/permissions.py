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

    def  has_object_permission(self, request, view, obj):
        # важно для ~IsModer в DestroyAPIView
        return self.has_permission(request, view)


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
