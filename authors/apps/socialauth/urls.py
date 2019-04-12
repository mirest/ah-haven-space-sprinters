
from django.urls import include, path
from django.conf.urls import url
from .views import SocialLoginAPIView, exchange_token

urlpatterns = [
    url(r'social/(?P<backend>[^/]+)/$', exchange_token),
    path('socials/<str:backend>/', SocialLoginAPIView.as_view()),

]
