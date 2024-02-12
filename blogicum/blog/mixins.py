from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from .models import Post
from .forms import PostForm


class PaginatePostViewMixin:
    """Базовый миксин для представлений модели Post."""

    paginate_by = settings.POSTS_ON_PAGE


class CreatePostViewMixin(LoginRequiredMixin):
    """Миксин для форм создания изменения и удаления постов."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class AlterPostViewMixin(CreatePostViewMixin):
    """Миксин для изменения и удаления постов."""

    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])

        if post.author != self.request.user:
            return redirect(
                "blog:post_detail", post_id=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)
