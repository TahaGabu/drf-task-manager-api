from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Only the user who created a Task may retrieve/update/delete it."""

    def has_object_permission(self, request, view, obj) -> bool:
        return obj.owner_id == request.user.id
