from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from authors.apps.profiles.models import Profile
from .models import Article
from .pagination import ArticleOffsetPagination
from .renderers import ArticleJSONRenderer
from .serializers import (
    ArticleSerializer
)


class ArticleView(ListCreateAPIView):
    """creating, viewing , deleting and updating articles"""

    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer
    pagination_class = ArticleOffsetPagination

    def post(self, request):
        serializer_context = {'author': request.user.profile}
        article = request.data

        # Create an article from the above data
        serializer = self.serializer_class(
            data=article, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticleRetrieveUpdateDelete(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    lookup_field = 'slug'

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Article, slug=slug)

    def destroy(self, request, slug):
        article = self.get_object(slug)
        requester = Profile.objects.get(user=request.user)
        is_author = article.author == requester
        if not is_author:
            resp = {"message": "you can't delete this article"}
            return Response(resp, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(article)
        resp = {"message": "Article has been deleted"}
        return Response(resp)

    def update(self, request, slug, *args, **kwargs):
        article = self.get_object(slug)
        requester = Profile.objects.get(user=request.user)
        is_author = article.author == requester
        if not is_author:
            resp = {"message": "you can't update this article"}
            return Response(resp, status=status.HTTP_403_FORBIDDEN)
        serializer_data = request.data
        serializer = self.serializer_class(
            article, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
