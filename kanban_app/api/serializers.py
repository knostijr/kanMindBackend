from django.contrib.auth import get_user_model
from rest_framework import serializers

from kanban_app.models import Board, Comment, Task

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    """
    Simplified User Serializer for nested representation.

    Used in Board, Task, and Comment serializers to display basic user information.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id', 'email', 'fullname']


class CommentSerializer(serializers.ModelSerializer):
    """
    Comment Serializer

    Response Format (aus API-Doku):
    {
        "id": 1,
        "created_at": "2025-02-20T14:30:00Z",
        "author": "Max Mustermann",
        "content": "Das ist ein Kommentar zur Task."
    }
    """
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        """_summary_

        Args:
            obj (_type_): _description_

        Returns:
            _type_: _description_
        """
        return obj.author.fullname


class TaskSerializer(serializers.ModelSerializer):
    """
    Task Serializer

    Request Format (aus API-Doku):
    {
        "board": 12,
        "title": "Code-Review durchführen",
        "description": "...",
        "status": "review",
        "priority": "medium",
        "assignee_id": 13,
        "reviewer_id": 1,
        "due_date": "2025-02-27"
    }
    
    Response Format:
    {
        "id": 10,
        "board": 12,
        "title": "Code-Review durchführen",
        "description": "...",
        "status": "review",
        "priority": "medium",
        "assignee": {
            "id": 13,
            "email": "marie.musterfraun@example.com",
            "fullname": "Marie Musterfrau"
        },
        "reviewer": {...},
        "due_date": "2025-02-27",
        "comments_count": 0
    }
    """
    assignee = UserSimpleSerializer(read_only=True)
    reviewer = UserSimpleSerializer(read_only=True)
    assignee_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True
    )
    reviewer_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True
    )
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'assignee_id',
            'reviewer',
            'reviewer_id',
            'due_date',
            'comments_count'
        ]
        read_only_fields = ['id', 'comments_count']
    
    def get_comments_count(self, obj):
        """
        Zähle Kommentare dieser Task
        """
        return obj.comments.count()
    
    def validate_assignee_id(self, value):
        """
        Prüfe ob assignee existiert
        """
        if value and not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Assignee not found")
        return value

    def validate_reviewer_id(self, value):
        """
        Prüfe ob reviewer existiert
        """
        if value and not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Reviewer not found")
        return value

    def create(self, validated_data):
        """
        Erstelle Task mit assignee_id und reviewer_id
        """
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)

        task = Task.objects.create(**validated_data)

        if assignee_id:
            task.assignee_id = assignee_id
        if reviewer_id:
            task.reviewer_id = reviewer_id

        task.save()
        return task

    def update(self, instance, validated_data):
        """
        Aktualisiere Task
        """
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)

        # Normale Felder aktualisieren
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # assignee_id und reviewer_id nur wenn im Request
        if 'assignee_id' in self.initial_data:
            instance.assignee_id = assignee_id
        if 'reviewer_id' in self.initial_data:
            instance.reviewer_id = reviewer_id

        instance.save()
        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """
    Board List Serializer

    Für GET /api/boards/ (Liste)

    Response Format (aus API-Doku):
    [
        {
            "id": 1,
            "title": "Projekt X",
            "member_count": 2,
            "ticket_count": 5,
            "tasks_to_do_count": 2,
            "tasks_high_prio_count": 1,
            "owner_id": 12
        }
    ]
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id'
        ]
        read_only_fields = ['id', 'owner_id']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Board Create Serializer

    for POST /api/boards/

    Request Formate example (compare API-Doku):
    {
        "title": "Neues Projekt",
        "members": [12, 5, 54, 2]
    }

    Response Format example:
    {
        "id": 18,
        "title": "neu",
        "member_count": 4,
        "ticket_count": 0,
        "tasks_to_do_count": 0,
        "tasks_high_prio_count": 0,
        "owner_id": 2
    }
    """
    members = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    
    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'members',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id'
        ]
        read_only_fields = ['id', 'owner_id']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()
    
    def create(self, validated_data):
        """
        Erstelle Board mit Members
        Owner wird in View gesetzt
        """
        member_ids = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        
        if member_ids:
            board.members.set(member_ids)
        
        return board


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Board Detail Serializer
    
    for GET /api/boards/{id}/
    
    Response Format example (compare API-Doku):
    {
        "id": 1,
        "title": "Projekt X",
        "owner_id": 12,
        "members": [
            {
                "id": 1,
                "email": "max.mustermann@example.com",
                "fullname": "Max Mustermann"
            }
        ],
        "tasks": [...]
    }
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserSimpleSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'owner_id']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Board Update Serializer
    
    for PATCH /api/boards/{id}/
    
    Request Format example (for API-Doku):
    {
        "title": "Changed title",
        "members": [1, 54]
    }
    
    Response Format example:
    {
        "id": 3,
        "title": "Changed title",
        "owner_data": {
            "id": 1,
            "email": "max.mustermann@example.com",
            "fullname": "Max Mustermann"
        },
        "members_data": [...]
    }
    """
    members = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    owner_data = UserSimpleSerializer(source='owner', read_only=True)
    members_data = UserSimpleSerializer(
        source='members',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members', 'members_data']
        read_only_fields = ['id', 'owner_data']
    
    def update(self, instance, validated_data):
        """
        board update
        
        Members werden ERSETZT (nicht hinzugefügt!)
        """
        member_ids = validated_data.pop('members', None)
        
        # Title update
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        
        # replace all members
        if member_ids is not None:
            instance.members.set(member_ids)
        
        return instance