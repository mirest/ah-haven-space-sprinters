from rest_framework import serializers
from .models import Profile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    first_name = serializers.CharField(allow_blank=True, required=False,
                                       min_length=2, max_length=50)
    last_name = serializers.CharField(allow_blank=True, required=False,
                                      min_length=2, max_length=50)
    bio = serializers.CharField(allow_blank=True, required=False)

    image = serializers.URLField(allow_blank=True, required=False)

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'created_at',
                  'bio', 'following', 'date_of_birth', 'image')

    @classmethod
    def get_username(self, obj):
        return f"{obj.user.username}"


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'bio', 'image', 'date_of_birth')

    @classmethod
    def get_username(self, obj):
        return f"{obj.user.username}"


class ProfileListSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'bio', 'image')

    @classmethod
    def get_username(self, obj):
        return f"{obj.user.username}"
