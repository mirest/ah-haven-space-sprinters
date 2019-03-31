from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, ActivationAPIView, ResetPasswordEmail,
    ResetPasswordConfirm
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name="updateRetrieve"),
    path('users/', RegistrationAPIView.as_view(), name='register'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
    path('users/<token>', ActivationAPIView.as_view(), name='verify'),
    path('password_reset/', ResetPasswordEmail.as_view(), name='password_reset'),
    path('reset/<str:uidb64>/<str:token>', ResetPasswordConfirm.as_view(), name='password_reset_confirm'),
]
