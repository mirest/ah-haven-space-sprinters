from django.urls import path

from .views import (
    UserProfileView,
    UserProfileUpdateView,
    UserProfileListView,
    FollowersAPIView,
    FollowDestroyAPIView,
    FollowCreateAPIView,
)

urlpatterns = [
    path(
        '<username>',
        UserProfileView.as_view(),
        name='profile-detail'),
    path(
        '<username>/edit',
        UserProfileUpdateView.as_view(),
        name='profile-update'),
    path(
        '',
        UserProfileListView.as_view(),
        name='profile-list'),
    path(
        '<username>/followers',
        FollowersAPIView.as_view(),
        name='get_followers'),
    path(
        '<username>/follow',
        FollowCreateAPIView.as_view(),
        name='follow_up'),
    path(
        '<username>/unfollow',
        FollowDestroyAPIView.as_view(),
        name='unfollow_up'),
]
