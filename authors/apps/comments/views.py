from .renderers import CommentRenderer, ReplyRenderer
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)
from .serializers import (
    CommentSerializer, ReplySerializer,
    CommentLikeSerializer
)
from ..profiles.models import Profile
from .models import Comment, Reply, CommentLike
from ..articles.models import Article
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from authors.apps.utilities.messages import error_messages


class CommentsAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer
    renderer_classes = (CommentRenderer,)

    def get(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        comments = Comment.objects.filter(article=article)
        serialize_data = self.serializer_class(comments, many=True)
        return Response({"comments": serialize_data.data},
                        status=status.HTTP_200_OK)

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        data = request.data
        author = Profile.objects.get(user=request.user)
        comment_on_start = request.data.get('comment_on_start')
        comment_on_end = request.data.get('comment_on_end')
        comment_on_text = None
        if comment_on_start and comment_on_end:
            if int(comment_on_start) < int(comment_on_end):
                highlight = [int(comment_on_start), int(comment_on_end)]
            else:
                highlight = [int(comment_on_end), int(comment_on_start)]
            comment_on_text = str(article.body[highlight[0]:highlight[1]])
        serializer = self.serializer_class(
            data=data, context={'article': article})
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=author,
            article=article,
            comment_on_text=comment_on_text
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer
    renderer_classes = (CommentRenderer,)

    def required_objects(self, request, slug, comment_pk):

        self.comment = get_object_or_404(Comment, pk=comment_pk)
        self.data = request.data

    def author_requirements(self, request):
        self.requester = Profile.objects.get(user=request.user)
        self.valid_author = self.comment.author == self.requester

    def get(self, request, slug, comment_pk):
        """gets one comment and its details"""
        comment = get_object_or_404(Comment, pk=comment_pk)
        serialize_data = self.serializer_class(comment)
        return Response(serialize_data.data, status=status.HTTP_200_OK)

    def patch(self, request, slug, comment_pk):
        self.required_objects(request, slug, comment_pk)
        self.author_requirements(request)
        article = get_object_or_404(Article, slug=slug)
        if not self.valid_author:
            raise PermissionDenied(
                error_messages.get('permission_denied'))

        serializer = self.serializer_class(
            self.comment, self.data, partial=True,
            context={'article': article}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, slug, comment_pk):
        raise PermissionDenied(
            {"error": "Method not implemented, use the patch method"})

    def delete(self, request, slug, comment_pk):
        self.required_objects(request, slug, comment_pk)
        self.author_requirements(request)

        if not self.valid_author:
            raise PermissionDenied(
                error_messages.get('permission_denied'))
        self.comment.delete()
        return Response({"message": "Successfully deleted comment"},
                        status=status.HTTP_200_OK)


class ReplyAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ReplySerializer
    renderer_classes = (ReplyRenderer,)

    def post(self, request, slug, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        data = request.data
        author = Profile.objects.get(user=request.user)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=author,
            comment=comment
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        replies = Reply.objects.filter(comment=comment)
        serialize_data = self.serializer_class(replies, many=True)
        return Response({"replies": serialize_data.data},
                        status=status.HTTP_200_OK)


class ReplyDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ReplySerializer
    renderer_classes = (ReplyRenderer,)

    def required_objects(self, request, slug, comment_pk, pk):
        self.reply = get_object_or_404(Reply, pk=pk)
        self.data = request.data

    def author_requirements(self, request):
        self.requester = Profile.objects.get(user=request.user)
        self.valid_author = self.reply.author == self.requester

    def get(self, request, slug, comment_pk, pk):
        """gets one reply and its details"""
        reply = get_object_or_404(Reply, pk=pk)
        serialize_data = self.serializer_class(reply)
        return Response(serialize_data.data, status=status.HTTP_200_OK)

    def patch(self, request, slug, comment_pk, pk):
        self.required_objects(request, slug, comment_pk, pk)
        self.author_requirements(request)

        if not self.valid_author:
            raise PermissionDenied(
                error_messages.get('permission_denied'))

        serializer = self.serializer_class(self.reply, self.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def put(self, request, slug, comment_pk, pk):
        raise PermissionDenied(
            {"error": "Method not implemented, use the patch method"})

    def delete(self, request, slug, comment_pk, pk):
        self.required_objects(request, slug, comment_pk, pk)
        self.author_requirements(request)

        if not self.valid_author:
            raise PermissionDenied(
                error_messages.get('permission_denied'))
        self.reply.delete()
        return Response({"message": "Successfully deleted reply"},
                        status=status.HTTP_200_OK)


class CommentLikeView(generics.GenericAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, *args, **kwargs):
        """
        like a specific comment
        Args:
            pk[integer]:primary key for a specific comment
        Returns:
            success message and 200 ok if complete else 404 if
            comment is not found
        """
        self.comment = get_object_or_404(Comment, pk=kwargs.get("pk"))
        self.userProfile = get_object_or_404(Profile, user=self.request.user)
        try:
            CommentLike.objects.get(liked_by=self.userProfile)
        except CommentLike.DoesNotExist:
            serializer = self.serializer_class(data={})
            serializer.is_valid(raise_exception=True)
            serializer.save(liked_by=self.userProfile,
                            comment=self.comment, like_status=True)
            return Response({
                "message": "comment liked successfully"
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "you already liked this comment"
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, *args, **kwargs):
        """
        get all likes of a comment

        Returns:
            likes count for a comment
            list of profiles that liked the comment
        """
        self.comment = get_object_or_404(Comment, pk=kwargs.get("pk"))
        self.likes = CommentLike.objects.filter(
            like_status=True).filter(comment=self.comment)
        serializer = self.serializer_class(self.likes, many=True)
        return Response({
            "likes": serializer.data,
            "likesCount": self.likes.count()
        }, status=status.HTTP_200_OK)

    def delete(self, *args, **kwargs):
        """
        delete a comment like provided you already liked it

        Returns:
            200 ok if unliking was successful and
            400 if user has not liked comment before
        """
        try:
            self.userProfile = get_object_or_404(
                Profile, user=self.request.user)
            self.comment = get_object_or_404(Comment, pk=kwargs.get("pk"))
            CommentLike.objects.get(liked_by=self.userProfile)
        except CommentLike.DoesNotExist:
            return Response({
                'message': 'you have not yet liked this comment'
            }, status=status.HTTP_400_BAD_REQUEST)
        CommentLike.objects.get(liked_by=self.userProfile).delete()
        return Response({
            "message": "unliked comment successfully"
        }, status=status.HTTP_200_OK)
