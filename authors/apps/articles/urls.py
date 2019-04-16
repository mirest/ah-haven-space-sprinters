from django.urls import path

from .views import (
    ArticleView, ArticleRetrieveUpdateDelete, ShareFacebookView,
    ShareTwitterView, ShareEmailView, Tagview
)

urlpatterns = [
    path('articles/', ArticleView.as_view(), name='create_article'),
    path('articles/<slug>', ArticleRetrieveUpdateDelete.as_view(), name='get_article'),
    path('articles/<slug>/share/facebook',
         ShareFacebookView.as_view(), name='share_facebook'),
    path('articles/<slug>/share/twitter',
         ShareTwitterView.as_view(), name='share_twitter'),
    path('articles/<slug>/share/email',
         ShareEmailView.as_view(), name='share_email'),
    path('tags/', Tagview.as_view(), name='get_tags'),

]
