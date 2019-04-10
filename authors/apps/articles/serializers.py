from rest_framework import serializers

from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import UserProfileSerializer
from authors.apps.utilities.estimators import article_read_time
from .models import Article


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
    author = AuthorProfileSerializer(read_only=True)
    image = serializers.URLField(allow_blank=True, required=False)
    read_time = serializers.SerializerMethodField()

    class Meta:
        model = Article
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['title', 'description', 'body', 'image', 'slug',
                  'favourited', 'created_at', 'updated_at', 'author',
                  'read_time', ]

    @classmethod
    def get_read_time(self, obj):
        return article_read_time(obj.body)

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
