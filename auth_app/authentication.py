from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.authtoken.models import Token


class CustomTokenAuthentication(BaseAuthentication):
    """
    Custom Token Authentication for API requests.

    Implementstoken authentication by parsing the Authorization header
    and validating tokens against the database.

    Usage:
        Authorization:  <token>
    """

    keyword = "Token"

    def authenticate(self, request):
        """
        Authenticate the request using Bearer token.

        Args:
            request: The HTTP request object

        Returns:
            tuple: (user, token) if authentication successful
            None: If no authentication attempted

        Raises:
            AuthenticationFailed: If authentication fails
        """
        # Get Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            return None

        # Parse "Bearer <token>"
        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token_key = parts[1]

        # Validate token against database
        try:
            token = Token.objects.select_related("user").get(key=token_key)

            # Check if user is active
            if not token.user.is_active:
                raise exceptions.AuthenticationFailed("User inactive or deleted")

            return (token.user, token)

        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token")
