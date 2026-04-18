from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

class CustomCookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # 1. Try to get the token from the header (Standard behavior)
        header = self.get_header(request)
        
        # 2. If it's not in the header, look inside the secure HttpOnly cookie
        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)

        # 3. If no token is found anywhere, reject the request
        if raw_token is None:
            return None

        # 4. If found, validate it and log the user in
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token