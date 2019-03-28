import jwt
from datetime import datetime, timedelta
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, GenericAPIView
import os
from django.conf import settings
from config.settings import default
from django.urls import reverse
from .backends import JWTAuthentication



from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.data['email']
        verification_token = serializer.data['auth_token']
        resp = RegistrationAPIView.verification_link(email,request,verification_token)
        return Response(resp, status=status.HTTP_201_CREATED)

    @staticmethod
    def verification_link(email,request,token):
        """
        method to send a verification link to a user
        """
        domain = request.get_host()
        url = reverse('auth:verify', kwargs={'token': token})
        link = f'{domain}{url}'
        subject = "Activation for your account"
        message = f'Please Activate your account below.\n{link}'
        from_mail = default.DEFAULT_FROM_EMAIL
        to_mail = [email]
        send_mail(subject, message, from_mail, to_mail, fail_silently=False)
        response_data = {
            "msg":'Please check your email to verify your account verification has been sent to {}'.format(email)
        }

        return response_data


class ActivationAPIView(GenericAPIView,JWTAuthentication):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def get(self,request,token):
        """
            Method to activate a user after they click link in their emails
        """
        user,token=self._authenticate_credentials(request,token)
        
        if user.is_valid==False:
            user.is_valid = True
            user.save()
            return Response ({"message":"youve been verified","status":200},status=status.HTTP_200_OK)
        else:
            return Response({'msg':'account has already been verified'},status=status.HTTP_400_BAD_REQUEST)
        


        
class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
