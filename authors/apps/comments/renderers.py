from ..authentication.default_renderer import BaseRenderer


class CommentRenderer(BaseRenderer):
    data = 'comment'


class ReplyRenderer(BaseRenderer):
    data = 'reply'
