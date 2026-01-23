from rest_framework import permissions
from rest_framework.exceptions import NotFound


class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Permission: User muss Owner oder Member des Boards sein
    
    Verwendet für: Board Detail (GET), Board Update (PATCH)
    
    WICHTIG: Prüft erst ob Board existiert (404), dann Permission (403)
    """
    def has_object_permission(self, request, view, obj):
        # Owner hat immer Zugriff
        if obj.owner == request.user:
            return True
        
        # Members haben Zugriff
        return obj.members.filter(id=request.user.id).exists()


class IsBoardOwner(permissions.BasePermission):
    """
    Permission: Nur Board-Owner
    
    Verwendet für: Board Delete (DELETE)
    
    WICHTIG: Prüft erst ob Board existiert (404), dann Permission (403)
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMember(permissions.BasePermission):
    """
    Permission: User muss Member des Task-Boards sein
    
    Verwendet für: Task Create, Task Update, Task Delete
    
    WICHTIG: Prüft erst ob Board existiert (404), dann Permission (403)
    """
    def has_permission(self, request, view):
        # Bei Create: Prüfe board_id im Request
        if request.method == 'POST':
            board_id = request.data.get('board')
            if not board_id:
                return False
            
            from kanban_app.models import Board
            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                # Board existiert nicht -> 404 (wird in View geworfen)
                raise NotFound("Board not found")
            
            # Prüfe ob User Member oder Owner ist
            is_member = (
                board.owner == request.user or
                board.members.filter(id=request.user.id).exists()
            )
            
            if not is_member:
                # User ist kein Member -> 403
                return False
            
            return True
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Bei Update/Delete: Prüfe Task-Board
        board = obj.board
        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )


class IsCommentAuthorOrBoardMember(permissions.BasePermission):
    """
    Permission: Comment darf nur von Board-Members gesehen werden
    
    Und nur Autor kann Comment löschen
    
    WICHTIG: Prüft erst ob Task/Comment existiert (404), dann Permission (403)
    """
    def has_permission(self, request, view):
        # Bei GET/POST: Prüfe ob User Member des Task-Boards ist
        task_id = view.kwargs.get('task_pk')
        if not task_id:
            return False
        
        from kanban_app.models import Task
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            # Task existiert nicht -> 404
            raise NotFound("Task not found")
        
        board = task.board
        is_member = (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )
        
        if not is_member:
            # User ist kein Member -> 403
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Bei DELETE: Nur Autor darf löschen
        if request.method == 'DELETE':
            return obj.author == request.user
        
        # Bei GET: Board-Member Check (wurde schon in has_permission gemacht)
        return True