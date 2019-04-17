import json

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView, GenericAPIView,
    RetrieveAPIView)
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from config.settings import default
from .models import Article, ArticleLikes
from .renderers import ArticleLikesRenderer, ArticleJSONRenderer
from .serializers import LikeArticleSerializer

from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
from authors.apps.articles.utilities import (
    get_likes_or_dislkes, get_like_status,
    get_usernames
)


class ArticleLikesView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleLikesRenderer,)
    serializer_class = LikeArticleSerializer
    queryset = ArticleLikes.objects.all()

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        article_like = ArticleLikes.objects.filter(
            article__slug=slug, user=self.request.user).first()
        if article_like:
            return article_like

    @classmethod
    def put(self, request, slug):
        """
        Updates the article with the reader's feedback

        args:
            request (Request object): Django Request context
            slug (Article label): stores and generates a valid URL for the
                                    article.

        Returns:
            HTTP Response message: A dictionary
            HTTP Status code: 201, 200
        """

        user = request.user
        article_id = get_object_or_404(Article, slug=slug)
        like_article = request.data.get('like_article', None)

        if like_article is None:
            raise serializers.ValidationError(
                'like_article field is required')

        if not isinstance(like_article, bool):
            raise serializers.ValidationError(
                'Value of like_article should be a boolean')

        try:
            like = ArticleLikes.objects.get(
                user=user, article=article_id, like_article=like_article)

            verb = get_like_status(like_article, 'liked', 'disliked')
            return Response(
                {'message': 'You have already {} the article'.
                    format(verb)},
                status=status.HTTP_200_OK)
        except ArticleLikes.DoesNotExist:
            like = ArticleLikes.objects.create(
                user=user, article=article_id, like_article=like_article)
            like.save()

            if ArticleLikes.objects.filter(
                user=user,
                article=article_id
            ).count() > 1:
                first_like = ArticleLikes.objects.get(
                    user=user,
                    article=article_id,
                    like_article=not like_article
                )
                first_like.delete()

            verb = get_like_status(like_article, 'liked', 'disliked')
            return Response(
                {'message': 'You have {} an article'.format(verb)},
                status=status.HTTP_201_CREATED)

    @classmethod
    def delete(self, request, slug):
        """
        Removes the reader's feedback on the article

        args:
            request (Request object): Django Request context
            slug (Article label): stores and generates a valid URL for the
                                    article.

        Returns:
            HTTP Response message
            HTTP Status code: 200
        """

        user = request.user
        article_id = get_object_or_404(Article, slug=slug)

        try:
            like_ = ArticleLikes.objects.get(
                user=user, article=article_id)
            like_article = ArticleLikes.objects.filter(
                user=user,
                article=article_id
            ).values('like_article')[0].get('like_article')
            like_.delete()
            verb = get_like_status(like_article, 'unliked', 'un-disliked')
            return Response(
                {'message': 'You have {} an article'.
                    format(verb)},
                status=status.HTTP_200_OK)
        except ArticleLikes.DoesNotExist:
            raise serializers.ValidationError(
                "There is no like or dislike to remove")

    @classmethod
    def get(self, request, slug):
        """
        Fetches a list of readers that gave feedback to an article

        args:
            request (Request object): Django Request context
            slug (Article label): stores and generates a valid URL for the
                                    article.

        Returns:
            HTTP Response message
            HTTP Status code: 200
        """

        article_id = get_object_or_404(Article, slug=slug)

        pleased_users = get_usernames(
            model=ArticleLikes,
            article_id=article_id,
            like_article=True
        )
        displeased_users = get_usernames(
            model=ArticleLikes,
            article_id=article_id,
            like_article=False
        )
        return Response(
            {'likes': pleased_users,
                'dislikes': displeased_users},
            status=status.HTTP_200_OK)
