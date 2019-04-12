from django.contrib.auth import login

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from social_django.utils import psa, load_strategy, load_backend
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.response import Response
from .serializer import AccessTokenSerializer



@api_view(http_method_names=['POST'])
@permission_classes([AllowAny])
@psa()
def exchange_token(request, backend):
    token = request.data.get('access_token')
    try:
        user = request.backend.do_auth(token)
    except Exception as e:
        return Response({"error": str(e)})
    if user:
        login(request, user)
        return Response({'email': user.email,
           'username': user.username,
           'auth_token': user.auth_token(),
       })
    return Response({"error":"unknown login error"})


class SocialLoginAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny,]
    serializer_class = AccessTokenSerializer

    @classmethod
    def post(self, request, backend, *args, **kwargs):
        token = request.data
        serializer = self.serializer_class(data=token)
        serializer.is_valid(raise_exception=True)
        request.social_strategy = load_strategy(request)
        try:
            request.backend = load_backend(request.social_strategy,backend, None)
            user = request.backend.do_auth(serializer.data.get('access_token'))
        except Exception as e:
            return Response({"error": str(e)})
        if user:
            login(request, user)
            return Response({'email': user.email,
               'username': user.username,
               'auth_token': user.auth_token(),
           })
        return Response({"error":"unknown login error"})
