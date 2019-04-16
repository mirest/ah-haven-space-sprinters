from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify


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
