import django_filters as filters

from .models import Task


class TaskFilter(filters.FilterSet):
    completed = filters.BooleanFilter(field_name="completed")
    priority = filters.ChoiceFilter(field_name="priority", choices=Task.Priority.choices)
    due_before = filters.DateFilter(field_name="due_date", lookup_expr="lte")
    due_after = filters.DateFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = ("completed", "priority", "due_before", "due_after")
