from django.urls import path

from .views import (
    ArticleView,
    ArticleRetrieveUpdateDelete,
    ShareFacebookView,
    ShareTwitterView,
    ShareEmailView,
    RatingCreateRetrieveAPIView,
    Tagview, ReportsAPIView,
    GetReportsAPIView,
    BookMarkCreateDestroyAPI,
    BookMarkRetrieveAPI,
)

from .like_views import ArticleLikesView
from .favourites_views import FavouritesView

urlpatterns = [
    path(
        'articles/',
        ArticleView.as_view(),
        name='create_article'),
    path(
        'articles/<slug>',
        ArticleRetrieveUpdateDelete.as_view(),
        name='get_article'),
    path(
        'articles/<slug>/share/facebook',
        ShareFacebookView.as_view(),
        name='share_facebook'),
    path(
        'articles/<slug>/share/twitter',
        ShareTwitterView.as_view(),
        name='share_twitter'),
    path(
        'articles/<slug>/share/email',
        ShareEmailView.as_view(),
        name='share_email'),
    path(
        'articles/<slug>/rate',
        RatingCreateRetrieveAPIView.as_view(),
        name='rate_article'),
    path('tags/', Tagview.as_view(), name='get_tags'),
    path('articles/<slug>/likes/',
         ArticleLikesView.as_view(), name='article_likes'),
    path('articles/<slug>/report/',
         ReportsAPIView.as_view(),
         name='report'),
    path('admin/report',
         GetReportsAPIView.as_view(), name='get_reports'),
    path(
        'articles/<slug>/bookmark',
        BookMarkCreateDestroyAPI.as_view(),
        name='bookmark_article'),
    path(
        'bookmarks',
        BookMarkRetrieveAPI.as_view(),
        name='bookmarked'),
    path(
        'articles/<slug>/favorite/',
        FavouritesView.as_view()),
    path(
        'articles/favorites/',
        FavouritesView.as_view(), name="favorited_articles"),
]
