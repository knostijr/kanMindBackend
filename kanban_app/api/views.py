from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
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
    permission_classes = []
    
    def get_queryset(self):
        """
        User sieht nur Boards wo er Owner oder Member ist
        """
        user = self.request.user
        return Board.objects.filter(
            owner=user
        ) | Board.objects.filter(
            members=user
        ).distinct()
    
    def get_serializer_class(self):
        """
        Wähle Serializer basierend auf Action
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
        Wähle Permissions basierend auf Action
        """
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAuthenticated(), IsBoardOwnerOrMember()]
        return [IsAuthenticated()]
    
    def get_object(self):
        """
        Überschreibe get_object um 404 VOR 403 zu werfen
        """
        queryset = Board.objects.all()  # NICHT get_queryset()!
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        
        try:
            obj = queryset.get(**filter_kwargs)
        except Board.DoesNotExist:
            # ERST 404 wenn Board nicht existiert
            raise NotFound("Board not found")
        
        # DANN Permission-Check (kann 403 werfen)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def perform_create(self, serializer):
        """
        Setze Owner automatisch auf aktuellen User
        """
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Task CRUD-Operationen
    
    Endpoints (aus API-Doku):
    - POST /api/tasks/ - Task erstellen
    - PATCH /api/tasks/{id}/ - Task aktualisieren
    - DELETE /api/tasks/{id}/ - Task löschen
    - GET /api/tasks/assigned-to-me/ - Mir zugewiesene Tasks
    - GET /api/tasks/reviewing/ - Tasks die ich reviewen soll
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]
    
    def get_queryset(self):
        """
        User sieht nur Tasks aus Boards wo er Member ist
        """
        user = self.request.user
        return Task.objects.filter(
            board__owner=user
        ) | Task.objects.filter(
            board__members=user
        ).distinct()
    
    def get_object(self):
        """
        Überschreibe get_object um 404 VOR 403 zu werfen
        """
        queryset = Task.objects.all()  # NICHT get_queryset()!
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        
        try:
            obj = queryset.get(**filter_kwargs)
        except Task.DoesNotExist:
            # ERST 404 wenn Task nicht existiert
            raise NotFound("Task not found")
        
        # DANN Permission-Check (kann 403 werfen)
        self.check_object_permissions(self.request, obj)
        return obj
    
    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        """
        GET /api/tasks/assigned-to-me/
        
        Gibt alle Tasks zurück wo User als assignee eingetragen ist
        
        Response Format (aus API-Doku):
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
        
        Gibt alle Tasks zurück wo User als reviewer eingetragen ist
        
        Response Format: Wie assigned_to_me
        """
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Comment CRUD-Operationen
    
    Endpoints (aus API-Doku):
    - GET /api/tasks/{task_id}/comments/ - Alle Comments einer Task
    - POST /api/tasks/{task_id}/comments/ - Comment erstellen
    - DELETE /api/tasks/{task_id}/comments/{id}/ - Comment löschen
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthorOrBoardMember]
    http_method_names = ['get', 'post', 'delete']  # Nur diese Methoden erlaubt
    
    def get_queryset(self):
        """
        Filtere Comments nach Task
        """
        task_id = self.kwargs.get('task_pk')
        
        # Prüfe ob Task existiert (404!)
        try:
            Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found")
        
        return Comment.objects.filter(task_id=task_id)
    
    def get_object(self):
        """
        Überschreibe get_object um 404 VOR 403 zu werfen
        """
        task_id = self.kwargs.get('task_pk')
        comment_id = self.kwargs.get('pk')
        
        # Prüfe ob Task existiert
        try:
            Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found")
        
        # Prüfe ob Comment existiert
        try:
            obj = Comment.objects.get(id=comment_id, task_id=task_id)
        except Comment.DoesNotExist:
            raise NotFound("Comment not found")
        
        # DANN Permission-Check (kann 403 werfen)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def perform_create(self, serializer):
        """
        Setze Author und Task automatisch
        """
        task_id = self.kwargs.get('task_pk')
        
        # Prüfe ob Task existiert (404!)
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task not found")
        
        serializer.save(
            author=self.request.user,
            task=task
        )