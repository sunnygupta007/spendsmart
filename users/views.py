from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.password_validation import validate_password # NEW
from django.core.exceptions import ValidationError as DjangoValidationError # NEW
from rest_framework import serializers

class CookieTokenObtainPairView(TokenObtainPairView):
    # Overwrite the default POST request to intercept the token
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            # Lock the Access Token in an HttpOnly Cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            
            # Lock the Refresh Token
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            
            # Delete the raw tokens from the JSON body for maximum security
            del response.data['access']
            del response.data['refresh']
            response.data['message'] = "Login successful. Tokens locked in secure cookies."

        return response

class LogoutAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # To log out, tell the browser to delete the cookies
        response = Response({"message": "Successfully logged out."})
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie('refresh_token')
        return response

# 1. A quick serializer to validate the new user data
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    # Force DRF to run Django's strict password rules
    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            # Pass the exact list of errors (e.g., "Too short") back to the frontend
            raise serializers.ValidationError(list(e.messages))
        return value

    # Prevent usernames like "12345"
    def validate_username(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Username cannot be entirely numeric.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# 2. The API view that accepts the POST request
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_api(request):
    """Returns the username of the user who owns the HttpOnly cookie"""
    return Response({
        'username': request.user.username
    })