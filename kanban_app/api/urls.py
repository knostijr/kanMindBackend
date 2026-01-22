from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import BoardViewSet, CommentViewSet, TaskViewSet

# Haupt-Router
router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tasks', TaskViewSet, basename='task')

# Nested Router für Task-Comments
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