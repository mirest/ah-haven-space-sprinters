from django_filters import FilterSet, rest_framework
from .models import Article


class FilterArticle(FilterSet):
    title = rest_framework.CharFilter('title', lookup_expr='icontains')

    author = rest_framework.CharFilter(
        'author__user__username', lookup_expr='icontains')

    tag = rest_framework.CharFilter('tags', lookup_expr='icontains')

    class Meta:

        model = Article
        fields = ('title', 'author', 'tag')
