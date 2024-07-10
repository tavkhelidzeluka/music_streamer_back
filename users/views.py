from django.shortcuts import render
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Create your views here.
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data['refresh']
        access = response.data['access']

        res = Response()
        res.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=True,  # Use secure=True in production
            samesite='Lax'
        )
        res.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=True,  # Use secure=True in production
            samesite='Lax'
        )
        res.data = {"message": "Login successful"}
        return res


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token missing'}, status=status.HTTP_400_BAD_REQUEST)

        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        access = response.data['access']

        res = Response()
        res.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=True,  # Use secure=True in production
            samesite='Lax'
        )
        res.data = {"message": "Token refreshed"}
        return res
