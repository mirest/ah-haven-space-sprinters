import json

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from config.settings import default
from .models import Favourites, Article
from .renderers import FavortiesJsonRenderer
from .serializers import FavouriteSerializer

from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User


class FavouritesView(RetrieveUpdateAPIView):
    """
    method class holding favoriting an article and
     getting for an article favorites
    """

    serializer_class = FavouriteSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (FavortiesJsonRenderer,)
    http_method_names = ['put', 'get']

    def get_object(self, **kwargs):
        article_slug = self.kwargs.get('slug')
        article_obj = get_object_or_404(Article, slug=article_slug)
        return article_obj

    def put(self, request, **kwargs):
        article = self.get_object()
        user = request.user
        article_id = article.id
        fav = Favourites.objects.filter(
            article_id=article_id, user=user
        ).first()
        if fav:
            current_count = article.favourite_count
            if fav.favourite:
                if current_count == 1:
                    article.favorited = False
                fav.favourite = False
                article.favourite_count = current_count - 1
                response_data = {
                    "message": "article has been unfavorited"
                }
            else:
                fav.favourite = True
                article.favourite_count = current_count + 1
                response_data = {
                    "message": "article has been favorited"
                }
            fav.save()
            article.save()
            return Response(response_data, status=200)

        else:
            serializer = self.serializer_class(data={}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user,
                            article=article, favourite=True)

            article.favourite_count = article.favourite_count + 1
            article.favorited = True
            article.save()

            return Response({"message": "article has been favorited"
                             }, status=200)

    @classmethod
    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Favourites.objects.filter(favourite=True, user=user)

        serializer = FavouriteSerializer(
            queryset, many=True, context={'request': request})

        if not serializer.data:
            return Response({
                "message": "No Article Favorited Yet"
            },
                status=status.HTTP_404_NOT_FOUND)
        return Response({"favoriteArticles": serializer.data},
                        status=status.HTTP_200_OK)
