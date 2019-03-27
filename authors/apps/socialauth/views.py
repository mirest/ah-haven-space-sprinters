from django.contrib.auth import login

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from social_django.utils import psa, load_strategy, load_backend
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from .serializer import SocialSerializer


class SocialLoginAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SocialSerializer

    @classmethod
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        request.social_strategy = load_strategy(request)
        try:
            request.backend = load_backend(
                request.social_strategy, serializer.data.get('backend'), None)
            user = request.backend.do_auth(serializer.data.get('access_token'))
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        if user:
            login(request, user)
            return Response({'email': user.email,
                             'username': user.username,
                             'auth_token': user.auth_token(),
                             }, status=status.HTTP_200_OK)
        return Response({"error": "unknown login error"},
                        status=status.HTTP_400_BAD_REQUEST)
