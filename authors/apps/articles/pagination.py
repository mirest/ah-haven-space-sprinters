from rest_framework.pagination import LimitOffsetPagination


class ArticleOffsetPagination(LimitOffsetPagination):
    """ Set articles to only 5 articles per page
    """

    default_limit = 5
    offset_query_param = "offset"
