import logging

logger = logging.getLogger(__name__)


class DebugAuthMiddleware:
    """
    Debug-Middleware um Auth-Header zu loggen
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log Authorization Header
        auth_header = request.META.get('HTTP_AUTHORIZATION', 'NO AUTH HEADER')
        print(f"🔍 Authorization Header: {auth_header}")
        print(f"🔍 Path: {request.path}")
        print(f"🔍 Method: {request.method}")
        
        # Log User
        print(f"🔍 User: {request.user}")
        print(f"🔍 Is Authenticated: {request.user.is_authenticated}")
        print("=" * 50)
        
        response = self.get_response(request)
        return response