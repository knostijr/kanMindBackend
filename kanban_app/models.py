from django.conf import settings
from django.db import models


class Board(models.Model):
    """
    Board Model

    Represents a project board owned by a user with a many-to-many relationship to members.
    """
    title = models.CharField(
        max_length=200,
        help_text="Board-Titel"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards",
        help_text="Board-Eigentümer"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="boards",
        blank=True,
        help_text="Board-Mitglieder"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Board'
        verbose_name_plural = 'Boards'

    def __str__(self):
        return self.title


class Task(models.Model):
    """
    Task Model

    Represents an item of work within a board, featuring 
    foreign key relationships to an assignee and a reviewer.
    """
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="Zugehöriges Board"
    )
    title = models.CharField(
        max_length=200,
        help_text="Task-Titel"
    )
    description = models.TextField(
        blank=True,
        help_text="Task-Beschreibung"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='to-do',
        help_text="Task-Status"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Task-Priorität"
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        help_text="Zugewiesener Bearbeiter"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="review_tasks",
        help_text="Zugewiesener Reviewer"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Fälligkeitsdatum"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f"{self.title} ({self.status})"


class Comment(models.Model):
    """
    Comment Model

    Represents a comment associated with a task, authored by a specific user.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Zugehörige Task"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Kommentar-Autor"
    )
    content = models.TextField(
        help_text="Kommentar-Inhalt"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return f"Comment by {self.author.fullname} on {self.task.title}"