from django.db.models import Count
from django.utils import timezone

from .models import Post


def post_query_default(manager=Post.objects, filters=False, annotate=False):
    """Функция собирающая основной запрос для модели пост."""
    queryset = manager.select_related(
        'author', 'location', 'category'
    )

    if filters:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    if annotate:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    return queryset
