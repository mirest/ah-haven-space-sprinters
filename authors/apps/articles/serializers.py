import datetime
from rest_framework import serializers
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Avg, Sum, Count, Func
from rest_framework.fields import CurrentUserDefault
from django.core.validators import MaxValueValidator, MinValueValidator
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
from authors.apps.profiles.serializers import UserProfileSerializer
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.utilities.estimators import article_read_time
from .models import Article, Rating, ArticleLikes, Report, BookMark


class AuthorProfileSerializer(UserProfileSerializer):
    class Meta:
        model = Profile
        fields = ('bio', 'username', 'image', 'following', )


class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()
    body = serializers.CharField()
    slug = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)
    favourited = serializers.CharField(read_only=True)
    rating = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    author = AuthorProfileSerializer(read_only=True)
    image = serializers.URLField(allow_blank=True, required=False)
    read_time = serializers.SerializerMethodField()
    user_like_status = serializers.SerializerMethodField()

    class Meta:
        model = Article
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['title', 'description', 'body', 'image', 'slug',
                  'favourited', 'created_at', 'updated_at', 'author',
                  'read_time', 'tags', 'rating', 'user_rating',
                  'likes_count', 'dislikes_count', 'user_like_status']

    @classmethod
    def get_read_time(self, obj):
        return article_read_time(obj.body)

    @classmethod
    def get_rating(self, obj):
        return obj.average_rating

    def get_user_like_status(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                user_like_status = ArticleLikes.objects.filter(
                    article=obj, user=user
                )
                return str(user_like_status.values_list('like_article')[
                    0][0] if user_like_status.exists() else 0)
        return None

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                rate = Rating.objects.filter(article=obj, user=user)
                return float(rate.values_list('rating')[
                             0][0] if rate.exists() else 0)
        return None

    def create(self, validated_data):
        author = self.context.get('author', None)
        return Article.objects.create(author=author, **validated_data)

    def update(self, instance, validated_data):
        """Performs an update on a Article"""
        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `Article` instance one at a time.
            setattr(instance, key, value)
        # Finally, after everything has been updated, we must explicitly save
        # save the model.
        instance.save()
        return instance


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.

        fields = ['email', ]


class RatingSerializer(serializers.ModelSerializer):
    """
    serializers class holding rating logic for an article
    """
    rating = serializers.DecimalField(
        required=True,
        max_digits=5,
        decimal_places=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)])

    @staticmethod
    def validate_user_rate(slug, user: User):
        article = get_object_or_404(Article, slug__exact=slug)
        rating = Rating.objects.filter(article__slug=slug, user=user)
        if article.author.user == user:
            raise serializers.ValidationError({
                "error": [
                    "Rate an article that does not belong to you, Please"]
            })
        elif rating.exists():
            raise serializers.ValidationError({
                "error": [
                    "Article rating already exists, Please"]
            })
        return article

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['article details:'] = ({
            'author': instance.article.author.user.username,
            'title': instance.article.title,
            'body': instance.article.body,
            'description': instance.article.description},)
        response['user'] = instance.user.username
        response['article'] = instance.article.slug
        response['average_rating'] = instance.article.average_rating
        return response

    class Meta:
        model = Rating
        fields = ("rating", "user", "article",)
        read_only_fields = ("user", "article",)


class LikeArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for liking an article model
    """
    like_article = serializers.BooleanField()

    class Meta:
        model = ArticleLikes
        fields = ('like_article', 'article', 'user')
        read_only_fields = ('article', 'user')


class ReportSerializer(serializers.ModelSerializer):

    """serializer for reporting articles"""

    reporter = serializers.SerializerMethodField()
    article_slug = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ('reporter', 'article_slug', 'reason',)

    @classmethod
    def get_article_slug(self, obj):
        return f"{obj.article.slug}"

    @classmethod
    def get_reporter(self, obj):
        return f"{obj.reporter.user.username}"


class BookMarkSerializer(serializers.ModelSerializer):
    """
    Serializer for bookmarking an article
    """

    class Meta:
        model = BookMark
        fields = ('article', 'user', 'bookmark')
        read_only_fields = ('article', 'user', 'bookmark')

    @staticmethod
    def create(slug, user: User):
        article = get_object_or_404(Article, slug=slug)
        bookmark = BookMark.objects.filter(article=article, user=user).exists()
        if bookmark:
            raise serializers.ValidationError({
                "error": [
                    "Article bookmark already exists, Please"]
            })
        elif user.is_authenticated and not bookmark:
            post = BookMark.objects.create(
                article=article, user=user, bookmark=True)
            return {
                'Article_slug': post.article.slug,
                'bookmark': post.bookmark}

    @staticmethod
    def delete(slug, user: User):
        article = get_object_or_404(Article, slug=slug)
        bookmark = BookMark.objects.filter(article=article, user=user).exists()
        if user.is_authenticated and bookmark:
            unbookmark = BookMark.objects.get(article=article, user=user)
            unbookmark.delete()
            return {'Article_slug': slug, 'bookmarked': False}
        elif not bookmark:
            raise serializers.ValidationError({
                "error": [
                    "Article bookmark doesnot exists."]
            })

    @staticmethod
    def get(user: User):
        bookmark = BookMark.objects.values_list(
            'article__slug', flat=True).filter(
            user=user)
        response = {'bookmarks': bookmark}
        return response
        fields = ('reporter', 'article_slug', 'reason',)

    @classmethod
    def get_article_slug(self, obj):
        return f"{obj.article.slug}"

    @classmethod
    def get_reporter(self, obj):
        return f"{obj.reporter.user.username}"


class AllReportsSerializer(serializers.ModelSerializer):

    """serializer for getting all reports"""
    reports = ReportSerializer(read_only=True, many=True)
    author = AuthorProfileSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ('slug', 'author', 'reports')
