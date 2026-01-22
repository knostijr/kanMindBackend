from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.models import Board, Comment, Task
from .permissions import (
    IsBoardMember,
    IsBoardOwner,
    IsBoardOwnerOrMember,
    IsCommentAuthor
)
from .serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskSerializer
)


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Board CRUD operations.

    Endpoints (from API documentation):
    - GET /api/boards/ - List all boards (Owner/Member)
    - POST /api/boards/ - Create a board
    - GET /api/boards/{id}/ - Board details
    - PATCH /api/boards/{id}/ - Update a board
    - DELETE /api/boards/{id}/ - Delete a board
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filters the queryset to return only boards where the current user 
        is the owner or a registered member.
        """
        user = self.request.user
        return Board.objects.filter(
            owner=user
        ) | Board.objects.filter(
            members=user
        ).distinct()
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class depending on the request action.
        """
        if self.action == 'list':
            return BoardListSerializer
        elif self.action == 'create':
            return BoardCreateSerializer
        elif self.action == 'retrieve':
            return BoardDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
        return BoardListSerializer
    
    def get_permissions(self):
        """
        Return the appropriate permission classes depending on the request action.
        """
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAuthenticated(), IsBoardOwnerOrMember()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """
        Assign the current user as the owner automatically during creation.
        """
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations.
    
    Endpoints (from API documentation):
    - POST /api/tasks/ - Create a task
    - PATCH /api/tasks/{id}/ - Update a task
    - DELETE /api/tasks/{id}/ - Delete a task
    - GET /api/tasks/assigned-to-me/ - Tasks assigned to me
    - GET /api/tasks/reviewing/ - Tasks I am assigned to review
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    def get_queryset(self):
        """
        Restrict queryset to tasks belonging to boards where the current user is a member.
        """
        user = self.request.user
        return Task.objects.filter(
            board__owner=user
        ) | Task.objects.filter(
            board__members=user
        ).distinct()
    
    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        """
        GET /api/tasks/assigned-to-me/
        
        Retrieve all tasks assigned to the current user.
        Response format matches the API documentation:
        
        [
            {
                "id": 1,
                "board": 1,
                "title": "Task 1",
                "description": "...",
                "status": "to-do",
                "priority": "high",
                "assignee": {...},
                "reviewer": {...},
                "due_date": "2025-02-25",
                "comments_count": 0
            }
        ]
        """
        tasks = Task.objects.filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def reviewing(self, request):
        """
        GET /api/tasks/reviewing/
        
        Retrieve the list of tasks where the current user is the designated reviewer.
        Response Format: Consistent with the assigned_to_me endpoint.
        """
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment CRUD operations.
    
    Endpoints (from API documentation):
    - GET /api/tasks/{task_id}/comments/ - List all comments for a task
    - POST /api/tasks/{task_id}/comments/ - Create a new comment
    - DELETE /api/tasks/{task_id}/comments/{id}/ - Delete a specific comment
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter comments based on the task_id provided in the URL.
        """
        task_id = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_id)
    
    def get_permissions(self):
        """
        Restrict comment deletion to the original author only.
        """
        if self.action == 'destroy':
            return [IsAuthenticated(), IsCommentAuthor()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """
        Automatically assign the current user as the author and link the comment to the specified task.
        """
        task_id = self.kwargs.get('task_pk')
        serializer.save(
            author=self.request.user,
            task_id=task_id
        )