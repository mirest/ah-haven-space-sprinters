from django.urls import path

from .views import (
    ArticleView, ArticleRetrieveUpdateDelete
)

urlpatterns = [
    path(
        'articles/',
        ArticleView.as_view(),
        name='create_article'),
    path(
        'articles/<slug>',
        ArticleRetrieveUpdateDelete.as_view(),
        name='get_article'),
]
