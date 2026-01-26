from django.contrib import admin
from .models import Board, Comment, Task


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin interface customization for Board models.
    """

    list_display = ["title", "owner", "created_at"]
    list_filter = ["owner", "created_at"]
    search_fields = ["title"]
    filter_horizontal = ["members"]
    date_hierarchy = "created_at"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface customization for Task models.
    """

    list_display = [
        "title",
        "board",
        "status",
        "priority",
        "assignee",
        "reviewer",
        "due_date",
    ]
    list_filter = ["status", "priority", "board"]
    search_fields = ["title", "description"]
    date_hierarchy = "created_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface customization for the Comment model.
    """

    list_display = ["author", "task", "content_preview", "created_at"]
    list_filter = ["author", "created_at"]
    search_fields = ["content"]
    date_hierarchy = "created_at"

    def content_preview(self, obj):
        """
        Return a truncated version of the content (first 50 characters).
        """
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"
