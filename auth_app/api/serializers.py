from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Basic User Serializer

    Used for user representation in responses.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id']


class RegistrationSerializer(serializers.Serializer):
    """
    Registration Serializer

    Request: fullname, email, password, repeated_password
    Response: token, fullname, email, user_id
    """
    fullname = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """
        Check if email already exists
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already registered"
            )
        return value

    def validate(self, attrs):
        """
        Check if both passwords match
        """
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({
                "password": "Passwords don't match"
            })
        return attrs

    def create(self, validated_data):
        """
        Create a new user

        Username is automatically generated from email
        (used only internally, not for login)
        """
        validated_data.pop('repeated_password')

        # automatically generate username
        username = validated_data['email'].split('@')[0]
        base_username = username
        counter = 1

        # ensure that username is unique
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )
        return user