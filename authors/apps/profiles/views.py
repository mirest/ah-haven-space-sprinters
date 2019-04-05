from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from authors.apps.utilities.custom_permissions.permissions import if_owner_permission
from .models import Follower
from .renderers import UserProfileJSONRenderer, UserProfileListRenderer
from .serializers import (
    UserProfileSerializer,
    ProfileUpdateSerializer,
    ProfileListSerializer,
    FollowerSerializer,
)


class UserProfileView(generics.RetrieveAPIView):
    """ Fetches and displays the details
    of a user profile to the currently
    logged in person
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    renderer_classes = (UserProfileJSONRenderer,)

    def get_object(self, *args, **kwargs):
        username = self.kwargs.get("username")
        return get_object_or_404(Profile, user__username=username)


class UserProfileUpdateView(generics.UpdateAPIView):
    """ Allows the currently logged in user
    to edit their user profile
    possible edittable fields include,
    first_name, last_name, bio
    and image """
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = (UserProfileJSONRenderer,)

    def get_object(self):
        if_owner_permission(self.request, **self.kwargs)
        username = self.kwargs.get("username")
        return get_object_or_404(Profile, user__username=username)


class UserProfileListView(generics.ListAPIView):
    """ Fetches and displays the author
    profiles with fields username,
    first_name, last_name, bio
    and image to the currently
    logged in person
    """
    serializer_class = ProfileListSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [UserProfileListRenderer, ]

    @classmethod
    def get_queryset(self):
        return Profile.objects.all()


class FollowersAPIView(generics.RetrieveAPIView):
    """A class for actors who request.user is following."""
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowerSerializer
    lookup_field = 'username'

    @classmethod
    def get(cls, request, username):
        # returns a list of actors who follow request.user
        following = Follower.objects.values_list(
            'follow', flat=True).filter(
            author=username)
        response = {'message': following, 'status_code': status.HTTP_200_OK}
        return Response(
            response,
            content_type='text/json',
            status=status.HTTP_200_OK)


class FollowCreateAPIView(generics.CreateAPIView):
    """A class for following other authors."""
    permission_classes = (IsAuthenticated,)
    lookup_field = 'username'
    serializer_class = FollowerSerializer

    @classmethod
    def post(cls, request, username):
        # Follow the author (where an author username=username).
        data = {'author': request.user.username, 'follow': username}
        serializer = cls.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        follow = Follower.objects.get_or_create(
            author=username, follow=request.user.username)
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.values().filter(user_id=user.pk)[0:]
        response = {'massage': {profile}, 'status_code': status.HTTP_200_OK}
        return Response(
            response,
            content_type='text/json',
            status=response['status_code'])


class FollowDestroyAPIView(generics.DestroyAPIView):
    """A class for unfollowing other authors."""
    permission_classes = (IsAuthenticated,)
    lookup_field = 'username'
    serializer_class = FollowerSerializer

    @classmethod
    def delete(cls, request, username):
        # Stop following the author (where an author username=username).
        unfollow = get_object_or_404(
            Follower,
            author=username,
            follow=request.user.username)
        unfollow.delete()
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.values().filter(user_id=user.pk)[0:]
        response = {'massage': profile, 'status_code': status.HTTP_200_OK}
        return Response(
            response,
            content_type='text/json',
            status=response['status_code'])
