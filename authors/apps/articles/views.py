import json

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    GenericAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from config.settings import default
from .models import Article, Rating, Report, BookMark
from .pagination import ArticleOffsetPagination
from .renderers import (
    ArticleJSONRenderer, ArticleShareLinkRenderer)
from .serializers import (
    ArticleSerializer,
    EmailSerializer,
    RatingSerializer,
    ReportSerializer,
    BookMarkSerializer,
    ArticleSerializer, EmailSerializer, RatingSerializer, ReportSerializer,
    AllReportsSerializer
)

from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
from .filters import FilterArticle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class ArticleView(ListCreateAPIView):
    """creating, viewing , deleting and updating articles"""

    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer
    pagination_class = ArticleOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filter_class = FilterArticle
    search_fields = ('description', 'body', 'title', 'author__user__username')

    def post(self, request):
        serializer_context = {'author': request.user.profile}
        article = request.data

        # Create an article from the above data
        serializer = self.serializer_class(
            data=article, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Tagview(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def all_tags():
        articles = get_list_or_404(Article)
        articles_with_tags = list(filter(lambda x: x.tags, articles))
        all_tags = []
        if articles_with_tags:
            all_tags_list = [x.tags for x in articles_with_tags]
            for tag in all_tags_list:
                all_tags += tag
            return set(all_tags)

    @staticmethod
    def get(request):
        tags = Tagview.all_tags()
        if tags:
            return Response({'tags': list(tags)}, status=status.HTTP_200_OK)
        return Response(
            {'message': 'there are no tags available'},
            status=status.HTTP_404_NOT_FOUND)


class ArticleRetrieveUpdateDelete(RetrieveUpdateDestroyAPIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer, )
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
            return Response(resp,
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(article)
        resp = {"message": "Article has been deleted"}
        return Response(resp)

    def update(self, request, slug, *args, **kwargs):

        article = self.get_object(slug)
        requester = Profile.objects.get(user=request.user)
        is_author = article.author == requester
        if not is_author:
            resp = {"message": "you can't update this article"}
            return Response(resp,
                            status=status.HTTP_403_FORBIDDEN)

        serializer_data = request.data
        serializer = self.serializer_class(
            article, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ShareFacebookView(APIView):
    """creating links for sharing articles via facebook
    """

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleShareLinkRenderer, )

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Article, slug=slug)

    def post(self, request, slug, *args, **kwargs):
        self.get_object(slug)
        current_url = 'https://{}'.format(get_current_site(request))
        route = 'api/articles'

        url = "{}/{}/{}".format(current_url, route, slug)

        facebook_url = "https://www.facebook.com/sharer/sharer.php?u="
        message = {"Facebook_link": facebook_url + url}

        return Response(message)


class ShareTwitterView(APIView):
    """creating links for sharing articles via facebook
    """

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleShareLinkRenderer, )

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Article, slug=slug)

    def post(self, request, slug, *args, **kwargs):
        self.get_object(slug)
        current_url = 'https://{}'.format(get_current_site(request))
        route = 'api/articles'

        url = "{}/{}/{}".format(current_url, route, slug)

        twitter_url = "https://twitter.com/home?status="
        message = {"twitter_link": twitter_url + url}

        return Response(message)


class ShareEmailView(CreateAPIView):
    """creating links for sharing articles via facebook
    """

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleShareLinkRenderer, )
    serializer_class = EmailSerializer

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Article, slug=slug)

    def post(self, request, slug, *args, **kwargs):
        reciever_mail = request.data
        serializer = self.serializer_class(data=reciever_mail)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        article = self.get_object(slug)
        title = article.title
        username = request.user.username
        current_url = 'https://{}'.format(get_current_site(request))
        route = 'api/articles'

        url = "{}/{}/{}".format(current_url, route, slug)

        from_email = default.DEFAULT_FROM_EMAIL
        to_mail = [email]
        subject = "Authors Haven"
        body = "{} shared an article about {}.\
             Click here to view article {}".format(
            username, title, url)
        send_mail(subject, body, from_email, to_mail, fail_silently=False)
        message = {"message": "Your article has been shared successfully"}

        return Response(message)


class RatingCreateRetrieveAPIView(CreateAPIView, RetrieveUpdateAPIView):
    """
    method class holding posting a rating for an article and
     getting an average rating for an article
    """
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticated, )
    renderer_classes = (ArticleJSONRenderer, )
    http_method_names = ['post', 'get', 'patch']

    def post(self, request, slug):
        data = request.data
        article = self.serializer_class.validate_user_rate(
            slug, request.user)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(article=article, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        data = get_object_or_404(
            Rating, article__slug=slug, user=request.user.pk)
        serializer = self.serializer_class(data, many=False)
        resp = {'rating': serializer.data['rating']}
        return Response(resp, status=status.HTTP_200_OK)

    def patch(self, request, slug):
        rate = get_object_or_404(
            Rating, article__slug=slug, user=request.user.pk)
        data = {'slug': slug, 'rating': request.data['rating']}
        serializer = self.serializer_class(rate, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportsAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer
    http_method_names = ['post']

    @staticmethod
    def can_create_report(reporter, article):
        message, status_code = None, None

        if reporter == article.author:
            message = "you cannot report your own article"
            status_code = status.HTTP_403_FORBIDDEN

        elif Report.objects.filter(reporter=reporter, article=article):
            message = "you already reported this article"
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        return message, status_code

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        reporter = get_object_or_404(Profile, user=request.user)

        message, status_code = ReportsAPIView.can_create_report(
            reporter, article)
        if message:
            return Response({"message": message}, status=status_code)

        serializer = self.serializer_class(
            data=request.data, context={'article': article})
        serializer.is_valid(raise_exception=True)
        serializer.save(
            reporter=reporter,
            article=article,
        )
        return Response({
            "msg": f"You have successfully reported article {article.slug}",
            "report": serializer.data},
            status=status.HTTP_201_CREATED)


class GetReportsAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AllReportsSerializer
    http_method_names = ['get']

    def get(self, request):
        user = request.user
        if user.is_superuser:
            reports = get_list_or_404(Report)
            article_reports = []
            for article_report in reports:
                report = get_object_or_404(
                    Article, id=article_report.article_id)
                article_reports.append(report)
            serializer_data = self.serializer_class(article_reports, many=True)
            return Response({"articles": serializer_data.data},
                            status=status.HTTP_200_OK)
        raise PermissionDenied(
            {"error": "permission denied login as admin"})


class BookMarkCreateDestroyAPI(CreateAPIView, DestroyAPIView):
    """
    method class holding bookmarking and un-bookmarking an article
    """
    serializer_class = BookMarkSerializer
    permission_classes = (IsAuthenticated, )
    renderer_classes = (ArticleJSONRenderer, )

    def post(self, request, slug):
        serializer = self.serializer_class.create(slug, request.user)
        return Response(serializer, status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        serializer = self.serializer_class.delete(slug, request.user)
        return Response(serializer, status=status.HTTP_200_OK)


class BookMarkRetrieveAPI(RetrieveAPIView):
    """
    method class holding getting bookmarked articles
    """
    serializer_class = BookMarkSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        serializer = self.serializer_class.get(request.user)
        return Response(serializer, status=status.HTTP_200_OK)
