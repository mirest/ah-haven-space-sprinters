from django.urls import path

from .views import (
    CommentDetailsAPIView, CommentsAPIView, ReplyAPIView, ReplyDetailsAPIView
)
urlpatterns = [
    path('<slug>/comments/', CommentsAPIView.as_view(), name='comments'),

    path('<slug>/comments/<comment_pk>',
         CommentDetailsAPIView.as_view(), name='specific_comment'),

    path('<slug>/comments/<comment_pk>/replies/',
         ReplyAPIView.as_view(), name='replies'),

    path('<slug>/comments/<comment_pk>/replies/<pk>',
         ReplyDetailsAPIView.as_view(), name='specific_reply')
]
