from rest_framework import permissions


class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Permission: User must be the owner or a member of the board.

    Used for: Board Detail (GET), Board Update (PATCH).
    """
    def has_object_permission(self, request, view, obj):
        # The owner is granted full access by default
        if obj.owner == request.user:
            return True

        # Members have access
        return obj.members.filter(id=request.user.id).exists()


class IsBoardOwner(permissions.BasePermission):
    """
    Permission: Board owner only.

    Used for: Board Delete (DELETE).
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMember(permissions.BasePermission):
    """
    Permission: User must be a member of the task board.

    Used for: Task Create, Task Update.
    """
    def has_permission(self, request, view):
        # For creation: Validate board_id provided in the request
        if request.method == 'POST':
            board_id = request.data.get('board')
            if not board_id:
                return False
            
            from kanban_app.models import Board
            try:
                board = Board.objects.get(id=board_id)
                return (
                    board.owner == request.user or
                    board.members.filter(id=request.user.id).exists()
                )
            except Board.DoesNotExist:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        # For Update/Delete: Verify the task's associated board
        board = obj.board
        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )


class IsCommentAuthor(permissions.BasePermission):
    """
    Permission: Only the comment author can delete.

    Used for: Comment Delete (DELETE).
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user