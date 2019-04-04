from rest_framework import serializers
from .models import Comment, Reply
from ..profiles import serializers as profiles


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
                  'updated_at', 'author', 'id', 'article', 'replies')
        read_only_fields = ('created_at', 'updated_at',
                            'authors', 'id', 'article')
