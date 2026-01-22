from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer, UserSerializer

User = get_user_model()


class RegistrationView(APIView):
    """
    POST /api/registration/

    create new user and give token back.

    Request:
        {
            "fullname": "Example Username",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword"
        }

    Response (201):
        {
            "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            "fullname": "Example Username",
            "email": "example@mail.de",
            "user_id": 1
        }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # create token
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

    Authenticates a user using email and password
    returns an authentication token

    Request:
        {
            "email": "example@mail.de",
            "password": "examplePassword"
        }

    Response (200):
        {
            "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            "fullname": "Example Username",
            "email": "example@mail.de",
            "user_id": 1
        }
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

        # searching for user with mail
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # check password
        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # get or create token
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
    check if email is existing and return data of user

    Response (200):
        {
            "id": 1,
            "email": "max.mustermann@example.com",
            "fullname": "Max Mustermann"
        }
    
    Response (404):
        {
            "error": "Email not found"
        }
    """
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
