from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.models import Board, Comment, Task
from .permissions import (
    IsBoardMember,
    IsBoardOwner,
    IsBoardOwnerOrMember,
    IsCommentAuthorOrBoardMember
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
    ViewSet für Board CRUD-Operationen

    Endpoints (aus API-Doku):
    - GET /api/boards/ - Liste aller Boards (Owner/Member)
    - POST /api/boards/ - Board erstellen
    - GET /api/boards/{id}/ - Board-Details
    - PATCH /api/boards/{id}/ - Board aktualisieren
    - DELETE /api/boards/{id}/ - Board löschen
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return boards where user is owner or member.
        """
        user = self.request.user

        # Apply distinct() to BOTH querysets before combining
        owner_boards = Board.objects.filter(owner=user).distinct()
        member_boards = Board.objects.filter(members=user).distinct()
    
        return owner_boards | member_boards

    def get_serializer_class(self):
        """
        choose Serializer due to action
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
        choose permissions depend of action
        """
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAuthenticated(), IsBoardOwnerOrMember()]
        return [IsAuthenticated()]

    def get_object(self):
        """
        overwrite get_object to get 404 before 403 zu werfen
        """
        queryset = Board.objects.all() 
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        try:
            obj = queryset.get(**filter_kwargs)
        except Board.DoesNotExist:
            raise NotFound("Board not found")
        # Check permissions after confirming object exists
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        """
        Set owner to current user when creating board.
        """
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Task CRUD-Operationen
    
    Endpoints (aus API-Doku):
    - POST /api/tasks/ - create Task 
    - PATCH /api/tasks/{id}/ - update Task 
    - DELETE /api/tasks/{id}/ - delete Task 
    - GET /api/tasks/assigned-to-me/ - assigned tasks
    - GET /api/tasks/reviewing/ - reviewing task
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def get_queryset(self):
        """
        User only see tasks where he is board owner
        """
        user = self.request.user
        
        owner_tasks = Task.objects.filter(board__owner=user).distinct()
        member_tasks = Task.objects.filter(board__members=user).distinct()
        
        return owner_tasks | member_tasks

    def get_object(self):
        """
        update get_object um 404 VOR 403 zu werfen
        """
        queryset = Task.objects.all()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        
        try:
            obj = queryset.get(**filter_kwargs)
        except Task.DoesNotExist:
            raise NotFound("Task not found")
        #  Permission-Check
        self.check_object_permissions(self.request, obj)
        return obj
    
    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        """
        GET /api/tasks/assigned-to-me/

        Returns all tasks where the user is assigned as the assignee.

        Response Format (from API-Doku):
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

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        """
        GET /api/tasks/reviewing/

        Returns all tasks where the user is assigned as reviewer.

        Response Format: Wie assigned_to_me
        """
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment CRUD operations

    Endpoints (from API documentation):
    - GET /api/tasks/{task_id}/comments/  Retrieve all comments for a task
    - POST /api/tasks/{task_id}/comments/ Create a comment
    - DELETE /api/tasks/{task_id}/comments/{id}/  Delete a comment
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthorOrBoardMember]
    http_method_names = ['get', 'post', 'delete'] 
    
    def get_queryset(self):
        """
        Retrieve comments associated with a task
        """
        task_id = self.kwargs.get('task_pk')
        
        # check if task existing (404!)
        try:
            Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found")
        
        return Comment.objects.filter(task_id=task_id)
    
    def get_object(self):
        """
        Ensure get_object raises 404 prior to permission checks
        """
        task_id = self.kwargs.get('task_pk')
        comment_id = self.kwargs.get('pk')
        
        # check if task is existing
        try:
            Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found")
        
        # check if Comment is existing
        try:
            obj = Comment.objects.get(id=comment_id, task_id=task_id)
        except Comment.DoesNotExist:
            raise NotFound("Comment not found")
        
        # Permission-Check (can 403 werfen)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def perform_create(self, serializer):
        """
        Auto-assign author and task
        """
        task_id = self.kwargs.get('task_pk')

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found")

        serializer.save(
            author=self.request.user,
            task=task
        )
