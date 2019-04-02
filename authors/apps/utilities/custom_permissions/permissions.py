from rest_framework.exceptions import PermissionDenied
from authors.apps.utilities.messages import error_messages


def if_owner_permission(request_obj, **kwargs):
    # Checks if user owns a resource

    if kwargs.get("username") != request_obj.user.username:
        raise PermissionDenied(
            error_messages.get('permission_denied'))
