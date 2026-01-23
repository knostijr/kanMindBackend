from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.authtoken.models import Token


class CustomTokenAuthentication(BaseAuthentication):
    """
    Custom Token Authentication - umgeht DRF's kaputte TokenAuthentication
    """
    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        # Parse "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0] != self.keyword:
            return None
        
        token_key = parts[1]
        
        # Suche Token DIREKT in DB
        try:
            token = Token.objects.select_related('user').get(key=token_key)
            
            if not token.user.is_active:
                raise exceptions.AuthenticationFailed('User inactive')
            
            print(f"✅ CustomTokenAuthentication SUCCESS!")
            print(f"   User: {token.user.email}")
            
            return (token.user, token)
            
        except Token.DoesNotExist:
            print(f"❌ Token nicht gefunden: {token_key}")
            raise exceptions.AuthenticationFailed('Invalid token')