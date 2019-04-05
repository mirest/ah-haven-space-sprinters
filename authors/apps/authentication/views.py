import json

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from config.settings import default
from .backends import JWTAuthentication
from .models import User
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
    ResetEmailSerializer,
    PasswordResetSerializer
)
from .tokens import password_rest_token


class RegistrationAPIView(CreateAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.data['email']
        verification_token = serializer.data['auth_token']
        resp = RegistrationAPIView.verification_link(
            email, request, verification_token)
        return Response(resp, status=status.HTTP_201_CREATED)

    @staticmethod
    def verification_link(email, request, token):
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
            "msg": 'Please check your email to verify your account verification has been sent to {}'.format(email)
        }

        return response_data


class ActivationAPIView(GenericAPIView, JWTAuthentication):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    renderer_classes = (UserJSONRenderer,)

    def get(self, request, token):
        """
            Method to activate a user after they click link in their emails
        """
        user, token = self._authenticate_credentials(request, token)

        if user.is_valid == False:
            user.is_valid = True
            user.save()
            return Response({"message": "youve been verified", "status": 200}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'account has already been verified'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data

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


class ResetPasswordEmail(CreateAPIView):
    """Password reset emailing with uid and reset token"""
    permission_classes = (AllowAny,)
    serializer_class = ResetEmailSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request, *args, **kwargs):
        """Returns message for reset password email"""
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            user = get_object_or_404(User, email=data['email'])
            current_site = get_current_site(request)
            token = password_rest_token.make_token(user),
            uidb64 = urlsafe_base64_encode(force_bytes(data['email'])).decode()
            body = json.dumps({
                'message': 'Please use the url below to rest your password,\
                            This expires after an hour, Thank you.',
                'domain': current_site.domain + f'/api/reset/{uidb64}/{token[0]}',
            })
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = data['email']
            subject = 'Confirm Your Article Account Password Reset'
            send_mail(subject, body, from_email, [
                      to_email], fail_silently=False)
            response = {'message': 'Please check your email to confirm rest password',
                        'status_code': status.HTTP_200_OK}
        except Exception as e:
            response = {'error': e, 'status_code': status.HTTP_400_BAD_REQUEST}
        return Response(response, content_type='text/json')


class ResetPasswordConfirm(CreateAPIView):
    """Password resetting with a provided uid and token"""

    serializer_class = PasswordResetSerializer
    renderer_classes = (UserJSONRenderer,)

    @classmethod
    def get_queryset(cls):
        return None

    def post(self, request, uidb64, token):
        """Returns Password reset success"""
        data = request.data
        if data['password1'] != data['password2']:
            response = {'error': 'Password donot match, try again',
                        'status_code': status.HTTP_400_BAD_REQUEST}
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, email=uid)
            auth = password_rest_token.check_token(user, token)
            serializer = self.serializer_class(auth, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            user.password = user.set_password(data['password1'])
            user.set_password(data['password1'])
            user.save()
            response = {'message': 'Password successfully updated',
                        'status_code': status.HTTP_200_OK}
        except Exception as e:
            response = {'error': 'Password reset failed',
                        'status_code': status.HTTP_400_BAD_REQUEST}
        return Response(response, content_type='text/json')
