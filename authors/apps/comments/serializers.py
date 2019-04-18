from rest_framework import serializers
from .models import Comment, Reply
from ..profiles import serializers as profiles
from rest_framework.exceptions import ValidationError


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

    class Meta:
        model = Comment
        fields = ('comment_body', 'created_at',
                  'updated_at', 'author', 'id', 'article', 'replies',
                  'comment_on_text', 'comment_on_start', 'comment_on_end')
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
