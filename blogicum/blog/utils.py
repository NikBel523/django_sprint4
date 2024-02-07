from django.utils import timezone

from .models import Post, User

# Вынес в отдельный фал, так как захотел выделить mixin.py,
# где также испоьзуется эта функция.


def base_posts_query(username=None):
    """Функция отвечающая за формирования основного запроса по постам."""
    base_query = Post.objects.select_related(
        'author', 'location', 'category'
    )

    if username:
        author_id = User.objects.get(username=username)
        base_query = base_query.filter(author__exact=author_id.pk)
    else:
        base_query = base_query.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    return base_query
