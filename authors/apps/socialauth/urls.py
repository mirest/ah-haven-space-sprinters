
from django.urls import path
from .views import SocialLoginAPIView

urlpatterns = [
    path('socials/', SocialLoginAPIView.as_view()),
]
