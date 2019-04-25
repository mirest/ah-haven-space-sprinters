from rest_framework import serializers
from .models import Comment, Reply, CommentLike
from ..profiles import serializers as profiles
from rest_framework.exceptions import ValidationError
from authors.apps.articles.serializers import AuthorProfileSerializer


class ReplySerializer(serializers.ModelSerializer):
    author = profiles.UserProfileSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = ('body', 'created_at', 'updated_at',
                  'author', 'id', 'comment')

        read_only_fields = ('created_at', 'updated_at',
                            'comment', 'author', 'id')


class CommentSerializer(serializers.ModelSerializer):

    author = profiles.UserProfileSerializer(read_only=True)
    replies = ReplySerializer(read_only=True, many=True)
    user_like_status = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('comment_body', 'created_at',
                  'updated_at', 'author', 'id', 'article', 'replies',
                  'comment_on_text', 'comment_on_start', 'comment_on_end',
                  'user_like_status', 'likes_count')
        read_only_fields = ('created_at', 'updated_at',
                            'authors', 'id', 'article', 'comment_on_text')

    def validate_comment_on_start(self, data):
        article_length = len(self.context['article'].body)
        if int(data) > article_length:
            raise ValidationError(
                "comment_on_start must not exceed article length"
            )

        return data

    def validate_comment_on_end(self, data):
        article_length = len(self.context['article'].body)
        if int(data) > article_length:
            raise ValidationError(
                "comment_on_end must not exceed article length"
            )

        return data

    def get_user_like_status(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                user_like_status = CommentLike.objects.filter(
                    comment=obj, user=user)
                return str(user_like_status.values_list('like_status')[
                    0][0] if user_like_status.exists() else 0)
        return None

    def get_likes_count(self,obj):
        self.comment = obj
        self.likes = CommentLike.objects.filter(
            like_status=True).filter(comment=self.comment)
        return self.likes.count()

class CommentLikeSerializer(serializers.ModelSerializer):
    liked_by = AuthorProfileSerializer(read_only=True)
    """
    A comment like serializer
    """
    class Meta:
        model = CommentLike
        fields = ('liked_by',)
        read_only_fields = ('like_status', 'liked_by')
