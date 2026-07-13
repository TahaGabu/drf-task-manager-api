from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .filters import TaskFilter
from .models import Task
from .permissions import IsOwner
from .serializers import TaskSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Tasks"],
        summary="List my tasks",
        description=(
            "Returns a paginated list of the authenticated user's tasks. "
            "Supports filtering by `completed`, `priority`, `due_before`, `due_after`, "
            "free-text `search` on title/description, and `ordering`."
        ),
    ),
    create=extend_schema(tags=["Tasks"], summary="Create a task"),
    retrieve=extend_schema(tags=["Tasks"], summary="Retrieve a task"),
    update=extend_schema(tags=["Tasks"], summary="Replace a task"),
    partial_update=extend_schema(tags=["Tasks"], summary="Partially update a task"),
    destroy=extend_schema(tags=["Tasks"], summary="Delete a task"),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for the `Task` resource, scoped to the authenticated user.

    - Every user only ever sees/edits their own tasks.
    - JWT bearer authentication is required for all actions.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = TaskFilter
    search_fields = ("title", "description")
    ordering_fields = ("created_at", "updated_at", "due_date", "priority")
    queryset = Task.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Task.objects.none()
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
