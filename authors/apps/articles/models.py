from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from authors.apps.authentication.models import User
from django.db.models import Avg, Sum, Count, Func
from django.utils.text import slugify
from ..profiles.models import Profile
from authors.apps.articles.utilities import (
    get_like_status, get_likes_or_dislkes
)


class Article(models.Model):
    # A tile for the created object
    title = models.CharField(max_length=120)

    # Each `Article` needs a human-readable unique identifier that we can use to
    # represent the `Article` in the UI. We want to index this column in the
    # database to improve lookup performance.
    slug = models.SlugField(
        db_index=True,
        max_length=255,
        unique=True,
        default=False)

    # A description for the created object
    description = models.TextField()

    # A body for the created object
    body = models.TextField()

    # An image field that will hold the names of the images added to the object
    image = models.URLField(blank=True, max_length=200, default="url")

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    # a field for articles marked as fovourites
    favourited = models.BooleanField(default=False)

    tags = ArrayField(
        models.CharField(max_length=300),
        blank=True, default=list)

    author = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        related_name='articles')

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Article.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super(Article, self).save(*args, **kwargs)

    @property
    def average_rating(self):
        ratings = self.ratings.all().aggregate(rating=Avg("rating"))
        return float('%.1f' % (ratings["rating"] if ratings['rating'] else 0))

    def likes_count(self):
        return get_likes_or_dislkes(
            model=ArticleLikes,
            like_article=True,
            article_id=self.pk
        )

    @property
    def dislikes_count(self):
        return get_likes_or_dislkes(
            model=ArticleLikes,
            like_article=False,
            article_id=self.pk
        )


class Rating(models.Model):
    article = models.ForeignKey(
        Article,
        related_name="ratings",
        on_delete=models.CASCADE,
        unique=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ratings",
        null=True,
        unique=False)
    rating = models.DecimalField(max_digits=5, decimal_places=1, validators=[
        MaxValueValidator(5), MinValueValidator(0)])

    class Meta:
        unique_together = ('article', 'user',)


class ArticleLikes(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        null=True, related_name="article_likes", blank=True)
    like_article = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Report(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        blank=True)
    reporter = models.ForeignKey(
        Profile, on_delete=models.CASCADE,
        blank=True)

    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article.slug


class BookMark(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bookmark = models.BooleanField(default=False)

    class Meta:
        unique_together = ('article', 'user',)
