import json
from rest_framework.renderers import JSONRenderer

from authors.apps.authentication.default_renderer import BaseRenderer


class UserProfileJSONRenderer(BaseRenderer):
    data = 'profile'


class UserProfileListRenderer(JSONRenderer):
    # Returns profiles of existing users
    charset = 'utf-8'
    data = 'profiles'

    @classmethod
    def render(self, data, media_type=None, renderer_context=None):
        # present a list of  user profiles in json format
        return json.dumps({
            self.data: data
        })


class FollowingJSONRenderer(BaseRenderer):
    data = 'follower'


class FollowingListRenderer(UserProfileListRenderer):
    # Returns followers of existing users
    data = 'followers'
