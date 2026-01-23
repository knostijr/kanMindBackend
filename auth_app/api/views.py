# Standardbibliothek
# (keine benötigt)

# Drittanbieter (Third-party)
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Lokale Importe
from .serializers import RegistrationSerializer, UserSerializer

User = get_user_model()


class RegistrationView(APIView):
    """
    POST /api/registration/
    
    Erstellt neuen User und gibt Token zurück.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Token erstellen
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """
    POST /api/login/
    
    Authentifiziert User mit email + password.
    Gibt Token zurück.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {"error": "Email and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # User mit Email suchen
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Passwort prüfen
        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Token holen oder erstellen
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "token": token.key,
            "fullname": user.fullname,
            "email": user.email,
            "user_id": user.id
        })


class EmailCheckView(APIView):
    """
    GET /api/email-check/?email=test@example.com
    
    Prüft ob Email existiert und gibt User-Daten zurück.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        email = request.query_params.get('email')
        
        if not email:
            return Response(
                {"error": "Email parameter required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response(
                {"error": "Email not found"},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_token(request):
    """
    GET /api/test-token/
    
    Test-Endpoint um zu prüfen ob Token-Authentication funktioniert.
    """
    return Response({
        "message": "✅ Token Authentication works!",
        "user_email": request.user.email,
        "user_id": request.user.id,
        "user_fullname": request.user.fullname
    })