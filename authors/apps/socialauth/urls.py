
from django.urls import include, path
from django.conf.urls import url
from .views import SocialLoginAPIView

urlpatterns = [
    path('socials/', SocialLoginAPIView.as_view()),

]
