from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import BoardViewSet, CommentViewSet, TaskViewSet

"""
URL configuration for the Board and Task API.
Includes nested routing for comments associated with specific tasks.
"""

# Main router for top-level resources
router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tasks', TaskViewSet, basename='task')

# Nested router for Task Comments
# This allows for URLs like /api/tasks/{task_pk}/comments/
tasks_router = routers.NestedDefaultRouter(
    router,
    r'tasks',
    lookup='task'
)
tasks_router.register(
    r'comments',
    CommentViewSet,
    basename='task-comments'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tasks_router.urls)),
]