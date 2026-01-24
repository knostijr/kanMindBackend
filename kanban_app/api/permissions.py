from rest_framework import permissions
from rest_framework.exceptions import NotFound


class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Permission: User must be an owner or member of the board.

    Used for: Board Detail (GET), Board Update (PATCH).

    IMPORTANT: First checks if the board exists (404), then checks permissions (403).
    """
    def has_object_permission(self, request, view, obj):
        # Owners always have access
        if obj.owner == request.user:
            return True

        # Members have access
        return obj.members.filter(id=request.user.id).exists()


class IsBoardOwner(permissions.BasePermission):
    """
    Permission: Board owner only.

    Used for: Board Delete (DELETE).

    IMPORTANT: First checks if the board exists (404), then checks permissions (403).
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMember(permissions.BasePermission):
    """
    Permission: User must be a member of the task's board.

    Used for: Task Create, Task Update, Task Delete.

    IMPORTANT: First checks if the board exists (404), then checks permissions (403).
    """
    def has_permission(self, request, view):
        # For Create: Check board_id in the request
        if request.method == 'POST':
            board_id = request.data.get('board')
            if not board_id:
                return False

            from kanban_app.models import Board
            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                # Board does not exist -> 404 (raised in view)
                raise NotFound("Board not found")

            # Check if user is member or owner
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
        # For Update/Delete: Check the task's board
        board = obj.board
        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )


class IsCommentAuthorOrBoardMember(permissions.BasePermission):
    """
    Permission: Comments can only be seen by board members.

    Additionally, only the author can delete the comment.

    IMPORTANT: First checks if Task/Comment exists (404), then checks permissions (403).
    """
    def has_permission(self, request, view):
        # For GET/POST: Check if user is a member of the task's board
        task_id = view.kwargs.get('task_pk')
        if not task_id:
            return False

        from kanban_app.models import Task
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            # Task does not exist -> 404
            raise NotFound("Task not found")

        board = task.board
        is_member = (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )

        if not is_member:
            # User is not a member -> 403
            return False

        return True
    
    def has_object_permission(self, request, view, obj):
        # For DELETE: Only the author is allowed to delete
        if request.method == 'DELETE':
            return obj.author == request.user
        
        # For GET: Board member check (already handled in has_permission)
        return True