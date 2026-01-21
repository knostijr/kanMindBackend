from rest_framework import permissions


class IsBoardOwnerOrMember(permissions.BasePermission):
    """
    Permission: User muss Owner oder Member des Boards sein

    Verwendet für: Board Detail (GET), Board Update (PATCH)
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
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMember(permissions.BasePermission):
    """
    Permission: User muss Member des Task-Boards sein

    Verwendet für: Task Create, Task Update
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
                return (
                    board.owner == request.user or
                    board.members.filter(id=request.user.id).exists()
                )
            except Board.DoesNotExist:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        # Bei Update/Delete: Prüfe Task-Board
        board = obj.board
        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )


class IsCommentAuthor(permissions.BasePermission):
    """
    Permission: Nur Comment-Autor kann löschen

    Verwendet für: Comment Delete (DELETE)
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user