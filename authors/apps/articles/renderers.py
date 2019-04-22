from authors.apps.authentication.default_renderer import BaseRenderer


class ArticleJSONRenderer(BaseRenderer):
    data = 'article'


class ArticleShareLinkRenderer(BaseRenderer):
    # Returns social media share links
    data = 'link'


class ArticleLikesRenderer(BaseRenderer):
    # Returns article like status
    data = 'like_status'
